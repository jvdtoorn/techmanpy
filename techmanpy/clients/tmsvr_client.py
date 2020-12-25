#!/usr/bin/env python

import asyncio

from .stateful_client import *
from ..packets import *
from ..exceptions import *

class TMSVR_client(StatefulClient):

   PORT=5891

   def __init__(self, *, robot_ip, client_id='SVRpy', conn_timeout=3):
      super().__init__(robot_ip=robot_ip, robot_port=self.PORT, client_id=client_id, conn_timeout=conn_timeout)
      self._client_id = client_id

   def _on_connection(self, reader, writer):
      return TMSVR_connection(self._client_id, reader, writer, self._conn_timeout)

class TMSVR_connection(StatefulConnection):

   def add_broadcast_callback(self, broadcast_callback):
      def parsed_callback(packet): broadcast_callback(TMSVR_packet(packet).items)
      super().add_broadcast_callback(parsed_callback)

   async def _execute(self, packet):
      # Submit
      res = TMSVR_packet(await self.send(packet))
      # Parse response
      assert res.handle_id == packet.handle_id
      if res.ptype == TMSVR_type.RESPONSE_STATUS and res.status != TMSVR_status.SUCCESS:
         if res.errdata is None: raise TMSVRError(res.errdesc)
         else: raise TMSVRError(f'{res.errdesc} (\'{res.errdata}\')')
      return res.items

   async def get_values(self, items):
      req = TMSVR_packet(self._obtain_handle_id(), TMSVR_type.VALUE_REQUEST, items)
      return await self._execute(req)

   async def get_value(self, key):
      try: return (await self.get_values({key}))[key]
      except KeyError: raise TMSVRError(f'Response did not contain value \'{key}\'')

   async def set_values(self, items):
      req = TMSVR_packet(self._obtain_handle_id(), TMSVR_type.VALUE_DATA, items)
      return await self._execute(req)

   async def set_value(self, key, value):
      return await self.set_values({key: value})
