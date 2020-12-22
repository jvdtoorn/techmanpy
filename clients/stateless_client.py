#!/usr/bin/env python

import asyncio

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class StatelessClient(TechmanClient):

   def __init__(self, *, robot_ip, robot_port):
      super(StatelessClient, self).__init__(robot_ip=robot_ip, robot_port=robot_port)
      self._request_callback = None

   def send(self, techman_packet): return self._loop.run_until_complete(self._send(techman_packet))
   async def _send(self, techman_packet):
      try:
         # Check connection
         if not self.is_connected and not await self._connect_async(): raise TechmanException('Could not connect to robot.')
         # Send packet
         self._writer.write(techman_packet.encoded())
         # Wait for response
         read_bytes = await self._reader.read(100000)
         res = TechmanPacket(read_bytes)
         # Validate response
         if res._header == 'CPERR': raise TechmanException(CPERR_packet(res).description)
         else: return res
      except TechmanException as e: raise e
      except Exception as e: raise TechmanException(str(e) + ' (' + type(e).__name__ + ')')

   def __del__(self):
      if hasattr(self, '_writer'):
         self._writer.close()

if __name__ == "__main__":

   clnt = StatelessClient(robot_ip='localhost', robot_port=5890)
   try:
      res = clnt.send(TMSTA_packet(TMSTA_type.QUEUE_TAG, [2]))
      print(res.encoded())
   except TechmanException as e: print(type(e).__name__ + ': ' + str(e))

   clnt._robot_ip='10.66.0.117'
   try:
      res = clnt.send(TMSTA_packet(TMSTA_type.QUEUE_TAG, [2]))
      print(res.encoded())
   except TechmanException as e: print(type(e).__name__ + ': ' + str(e))
