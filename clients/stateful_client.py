#!/usr/bin/env python

import asyncio

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class StatefulClient(TechmanClient):

   def __init__(self, suppress_warn=False, broadcast_callback=None, conn_timeout=None, *, robot_ip, robot_port):
      super(StatefulClient, self).__init__(robot_ip=robot_ip, robot_port=robot_port, conn_timeout=conn_timeout, suppress_warn=suppress_warn)
      self._broadcast_callback = broadcast_callback
      self._in_listen = False
      self._reconnect_cnt = 0
      self._requests = [] # request: [req, callback, age]
      if self._broadcast_callback is not None: self._start_listen()

   def send(self, techman_packet, callback=None): return self._loop.run_until_complete(self._send(techman_packet, callback=callback))
   async def _send(self, techman_packet, callback):
      if not self.is_connected and not await self._connect_async():
         exc = TechmanException(str(self._conn_exception) + ' (' + type(self._conn_exception).__name__ + ')')
         if callback is not None: callback(exc); return
         else: raise exc
      # Setup synchronous callback
      run_async = callback is not None
      res_future = asyncio.Future()
      def sync_callback(res):
         if isinstance(res, TechmanException): res_future.set_exception(res)
         else: res_future.set_result(res)
      if not run_async: callback = sync_callback
      # Send message
      self._requests.append([techman_packet, callback, 0])
      if not self._in_listen: self._start_listen()
      self._writer.write(techman_packet.encoded())
      # Block until result if sync
      if not run_async: return await res_future

   def _on_exception(self, exc):
      if not isinstance(exc, TechmanException):
         exc = TechmanException(str(exc) + ' (' + type(exc).__name__ + ')')
      for request in self._requests: request[1](exc)
      self._requests = []

   def _on_message(self, techman_packet):
      assert isinstance(techman_packet, StatefulPacket)
      # Check if this is a response to ongoing request
      handle_id = techman_packet.handle_id
      index, callback = -1, None
      for i, request in enumerate(self._requests):
         if request[0].handle_id != handle_id: continue
         index, callback = i, request[1]      
      # Call request callback
      if index != -1:
         del self._requests[index]
         callback(techman_packet)
      # Call broadcast callback
      elif self._broadcast_callback is not None: self._broadcast_callback(techman_packet)

   def _start_listen(self): self._listen_task = asyncio.gather(self._listen(), return_exceptions=False)
   async def _listen(self):
      self._in_listen = True
      while True:
         if not self.is_connected and not await self._connect_async():
            if self._broadcast_callback is None: self._on_exception(self._conn_exception); break
            else:
               if not self._suppress_warn: print('[StatefulClient] WARN: Broadcast server not connected, will try again in 3 seconds...')
               await asyncio.sleep(3)
               continue
         read_bytes = await self._reader.read(100000)
         # Ignore broken message (empty, or doesn't start with '$' or doesn't end with checksum)
         if read_bytes == b'':
            if self._reconnect_cnt > 10:
               self._reconnect_cnt = 0
               if not self.is_connected: self._on_exception(self._conn_exception)
               else: self._on_exception(TechmanException('Server is sending invalid data'))
               break
            self._conn_exception = TechmanException('Server is closed')
            self._reconnect_cnt += 1
            continue
         elif len(read_bytes) > 5 and (read_bytes[0] != 0x24 or read_bytes[-5] != 0x2A): continue
         self._reconnect_cnt = 0
         res = StatefulPacket(read_bytes)
         if res._header == 'CPERR':
            self._handle_exception(TechmanException(CPERR_packet(read_bytes).description))
            break
         self._on_message(res)
         # Refresh request if no answer within 5 packets
         for request in self._requests:
            request[2] += 1
            if request[2] > 5:
               request[2] = 0
               self._writer.write(request[0].encoded())
         if self._broadcast_callback is None and len(self._requests) == 0: break
      self._in_listen = False

   def __del__(self):
      if hasattr(self, '_writer'):
         self._writer.close()
