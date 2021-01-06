#!/usr/bin/env python

import asyncio
from asyncio import CancelledError

from .techman_client import *
from ..packets import *
from ..exceptions import *

class StatelessClient(TechmanClient):

   def _on_connection(self, reader, writer):
      return StatelessConnection(reader, writer, self._conn_timeout)

class StatelessConnection(TechmanConnection):

   async def send(self, packet):
      try:
         # Send packet
         self._writer.write(packet.encoded())
         await self._writer.drain()
         # Wait for response
         read_bytes = await asyncio.wait_for(self._reader.read(100000), timeout=self._conn_timeout)
         # Empty byte indicates lost connection
         if read_bytes == b'': raise TMConnectError(None, msg='Socket connection was closed by server')
         # Validate response
         res = StatelessPacket(read_bytes)
         if res._header == 'CPERR': raise TMProtocolError(CPERR_packet(res).description)
         else: return res
      except CancelledError as e: raise e # Delegate asyncio exception
      except TechmanException as e: raise e
      except asyncio.TimeoutError: raise TMConnectError(None, msg='Did not receive a message from server') from None
      except ConnectionError as e: raise TMConnectError(e) from None
      except RuntimeError as e:
         if 'coroutine' in str(e): raise TMConnectError(None, msg='Only one stateless outgoing request can be active at any time!') from None
