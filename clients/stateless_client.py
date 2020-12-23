#!/usr/bin/env python

import asyncio, asyncio.futures as futures

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class StatelessClient(TechmanClient):

   async def __init__(self, suppress_warn=False, conn_timeout=3, *, robot_ip, robot_port):
      await super(StatelessClient, self).__init__(robot_ip=robot_ip, robot_port=robot_port, conn_timeout=conn_timeout, suppress_warn=suppress_warn)
      self._request_callback = None

   async def send(self, techman_packet):
      try:
         # Check connection
         if not self.is_connected and not await self._connect_async(): raise TechmanException('Could not connect to robot.')
         # Send packet
         self._writer.write(techman_packet.encoded())
         # Wait for response
         read_fut = self._reader.read(100000)
         read_bytes = await asyncio.wait_for(read_fut, timeout=self._conn_timeout)
         # Empty byte indicates lost connection
         if read_bytes == b'': raise TechmanException('Socket connection was claimed by another client')
         res = StatelessPacket(read_bytes)
         # Validate response
         if res._header == 'CPERR': raise TechmanException(CPERR_packet(res).description)
         else: return res
      except TechmanException as e: raise e
      except asyncio.TimeoutError: raise TechmanException('Could not connect to robot.') from None
      except RuntimeError as e:
         if 'coroutine' in str(e): raise TechmanException('Only one stateless outgoing request can be active at any time!') from None
         else: raise e
      except Exception as e: raise TechmanException(str(e) + ' (' + type(e).__name__ + ')')
