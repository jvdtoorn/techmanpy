#!/usr/bin/env python

import asyncio

from .stateless_client import *
from ..packets import *
from ..exceptions import *

class TMSTA_client(StatelessClient):

   PORT=5890

   def __init__(self, *, robot_ip, conn_timeout=3):
      super().__init__(robot_ip=robot_ip, robot_port=self.PORT, conn_timeout=conn_timeout)

   def _on_connection(self, reader, writer):
      return TMSTA_connection(reader, writer, self._conn_timeout)

class TMSTA_connection(StatelessConnection):

   async def is_listen_node_active(self):
      # Build TMSTA packet
      req = TMSTA_packet(TMSTA_type.IN_LISTEN_MODE, None)
      # Submit
      res = TMSTA_packet(await self.send(req))
      # Parse response
      assert res.ptype == TMSTA_type.IN_LISTEN_MODE
      return res.params[0]

   async def get_queue_tag_status(self, tag_id):
      # Build TMSTA packet
      req = TMSTA_packet(TMSTA_type.QUEUE_TAG, [tag_id])
      # Submit
      res = TMSTA_packet(await self.send(req))
      # Parse response
      assert res.ptype == TMSTA_type.QUEUE_TAG
      return res.params[1]
