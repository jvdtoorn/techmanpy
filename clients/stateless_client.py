#!/usr/bin/env python

import asyncio

from techman_client import TechmanClient, TechmanConnection

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *
from util.exceptions import * # pylint: disable=no-name-in-module

class StatelessClient(TechmanClient):

   def _on_connection(self, reader, writer):
      return StatelessConnection(reader, writer, self._conn_timeout, self._suppress_warn)

class StatelessConnection(TechmanConnection):

   async def send(self, packet):
      try:
         # Send packet
         self._writer.write(packet.encoded())
         await self._writer.drain()
         # Wait for response
         read_bytes = await asyncio.wait_for(self._reader.read(100000), timeout=self._conn_timeout)
         # Empty byte indicates lost connection
         if read_bytes == b'': raise TMConnectError(None, msg='Socket connection was claimed by another client')
         # Validate response
         res = StatelessPacket(read_bytes)
         if res._header == 'CPERR': raise TMProtocolError(CPERR_packet(res).description)
         else: return res
      except TechmanException as e: raise e
      except asyncio.TimeoutError: raise TMConnectError(None, msg='Did not receive a message from server') from None
      except ConnectionError as e: raise TMConnectError(e)
      except RuntimeError as e:
         if 'coroutine' in str(e): raise TMConnectError(None, msg='Only one stateless outgoing request can be active at any time!') from None
         else: raise TechmanException()
      except Exception as e: raise TechmanException()
