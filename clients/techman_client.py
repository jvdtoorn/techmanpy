#!/usr/bin/env python

import asyncio
from concurrent.futures import ProcessPoolExecutor

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TechmanException(Exception):
   pass

class TechmanClient:

   def __init__(self, *, robot_ip, robot_port):
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._reconnect_cnt = 0
      self._outgoing_requests = []
      self._conn_exception = None
      self._loop = asyncio.get_event_loop()
      if not self._connect():
         print('[TechmanClient] WARN: Could not connect to robot during initialisation.')
      self._listen_task = self._loop.create_task(self._listen())

   def _connect(self): return self._loop.run_until_complete(self._connect_async())
   async def _connect_async(self):
      try: self._reader, self._writer = await asyncio.open_connection(self._robot_ip, self._robot_port)
      except Exception as e:
         self._conn_exception = e
         return False
      self._conn_exception = None
      return True

   def send(self, techman_packet, callback=None):
      res = self._loop.run_until_complete(self._send(techman_packet, callback=callback))
      if callback is None and isinstance(res, Exception):
         raise TechmanException(str(res) + ' (' + type(res).__name__ + ') ')
      else: return res

   async def _send(self, techman_packet, callback=None):
      # Setup synchronous callback
      run_async = callback is not None
      res_future = asyncio.Future()
      def sync_callback(packet): res_future.set_result(packet)
      if not run_async: callback = sync_callback

      # Run class-specific queue setup
      self._handle_outgoing(techman_packet, callback if run_async else sync_callback)

      if not self.is_connected: await self._connect_async()
      # Send message if connected
      if self.is_connected:
         self._writer.write(techman_packet.encoded())
         if not run_async: return await res_future
      # Send exception if not connected
      else:
         self._handle_exception(self._conn_exception)

   def _handle_exception(self, exc):
      for request in self._outgoing_requests:
         request[1](exc)
      self._outgoing_requests = []

   def _handle_incoming(self, packet):
      if len(self._outgoing_requests) == 0: return
      callback = self._outgoing_requests[0][1]
      self._outgoing_requests = []
      # Execute callback with received packet
      callback(packet)

   def _handle_outgoing(self, packet, callback):
      assert len(self._outgoing_requests) == 0
      self._outgoing_requests = [(None, callback)]

   async def _listen(self):
      while True:
         if not self.is_connected:
            if not await self._connect_async():
               # Notify requests that no connection is in place
               if len(self._outgoing_requests) > 0: self._handle_exception(self._conn_exception)
               print('[TechmanClient] WARN: Not connected. Trying again in 3 seconds')
               await asyncio.sleep(3)
               continue
         read_bytes = await self._reader.read(100000)
          # Ignore broken message (doesn't start with '$' or doesnt end with checksum)
         if read_bytes[0] != 0x24 or read_bytes[-5] != 0x2A: continue
         if read_bytes == b'':
            if self._reconnect_cnt > 5:
               self._reconnect_cnt = 0
               print('[TechmanClient] ERROR: Server is sending invalid responses, quitting listen loop.')
               return
            self._conn_exception = TechmanException('Connection was closed by server')
            self._reconnect_cnt += 1
            continue
         self._reconnect_cnt = 0
         res = TechmanPacket(read_bytes)
         if res._header == 'CPERR':
            print('[TechmanClient] ERROR: %s' % CPERR_packet(res).description)
            self._handle_exception(TechmanException(CPERR_packet(res).description))
         self._handle_incoming(res)

   @property
   def is_connected(self): return self._conn_exception is None

   def __del__(self):
      if hasattr(self, '_writer'):
         self._writer.close()      
      self._listen_task.cancel()
      self._loop.close()

if __name__ == "__main__":
   def callback(res):
      if isinstance(res, Exception):
         print(str(res) + ' (' + type(res).__name__ + ') ')
      else: print(f'received: {res.encoded()}')
      asyncio.get_event_loop().stop()

   clnt = TechmanClient(robot_ip='10.66.0.117', robot_port=5891)
   # clnt.send(TMSTA_packet(TMSTA_type.QUEUE_TAG, [1]), callback=callback)
   asyncio.get_event_loop().run_forever()

   # clnt._robot_ip='10.66.0.117'

   # try:
   #    packet = clnt.send(TMSTA_packet(TMSTA_type.QUEUE_TAG, [1]))
   #    print(f'received: {packet.encoded()}')
   # except TechmanException as e: print(type(e).__name__ + ': ' + str(e))