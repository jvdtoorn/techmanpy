#!/usr/bin/env python

import asyncio

from stateful_client import StatefulClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *
from util.exceptions import * # pylint: disable=no-name-in-module

class TMSVR_client(StatefulClient):

   PORT=5891

   async def __init__(self, suppress_warn=False, conn_timeout=3, id='SVRpy', broadcast_callback=None, *, robot_ip):
      if broadcast_callback is not None:
         callback = broadcast_callback
         def parsed_callback(res):
            if isinstance(res, Exception): callback(res)
            else: callback(TMSVR_packet(res))
         broadcast_callback = parsed_callback
      await super(TMSVR_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT, broadcast_callback=broadcast_callback, conn_timeout=conn_timeout, suppress_warn=suppress_warn)
      self._id = str(id)
      self._msg_cnt = 0

   def keep_alive(self): asyncio.get_event_loop().run_forever()

   def _execute(self, packet):
      # Submit
      res = TMSVR_packet(self.send(packet))
      # Parse response
      assert res.handle_id == packet.handle_id
      if res.ptype == TMSVR_type.RESPONSE_STATUS and res.status != TMSVR_status.SUCCESS:
         if res.errdata is None: raise TMSVRException(res.errdesc)
         else: raise TMSVRException('%s (name: %s)' % (res.errdesc, res.errdata))
      return res.items

   def get_values(self, items):
      # Build TMSVR packet
      handle_id = '%s%d' % (self._id, self._msg_cnt)
      self._msg_cnt += 1
      req = TMSVR_packet(handle_id, TMSVR_type.VALUE_REQUEST, items)
      # Submit
      return self._execute(req)

   def get_value(self, key):
      return self.get_values({key})[key]

   def set_values(self, items):
      # Build TMSVR packet
      handle_id = '%s%d' % (self._id, self._msg_cnt)
      self._msg_cnt += 1
      req = TMSVR_packet(handle_id, TMSVR_type.VALUE_DATA, items)
      # Submit
      return self._execute(req)

   def set_value(self, key, value):
      return self.set_values({key: value})
