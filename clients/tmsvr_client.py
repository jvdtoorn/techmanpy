#!/usr/bin/env python

import asyncio

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TMSVRException(TechmanException):
   pass

class TMSVR_client(TechmanClient):

   PORT=5891

   def __init__(self, *, robot_ip, id):
      super(TMSVR_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT)
      self._id = str(id)
      self._msg_cnt = 0

   def get_values(self, items):
      # Build TMSVR packet
      handle_id = '%s_%d' % (self._id, self._msg_cnt)
      self._msg_cnt += 1
      req = TMSVR_packet(handle_id, TMSVR_type.READ_REQUEST, items)
      # Submit
      res = TMSVR_packet(self.send(req))
      # Parse response
      assert res.handle_id == handle_id
      assert res.ptype == TMSVR_type.READ_RESPONSE
      return res.items

   def get_value(self, key):
      return self.get_values({key})

   def set_values(self, items):
      # Build TMSVR packet
      handle_id = '%s_%d' % (self._id, self._msg_cnt)
      self._msg_cnt += 1
      req = TMSVR_packet(handle_id, TMSVR_type.WRITE_REQUEST, items)
      # Submit
      res = TMSVR_packet(self.send(req))
      # Parse response
      assert res.handle_id == handle_id
      assert res.ptype == TMSVR_type.WRITE_RESPONSE
      if res.status != TMSVR_status.SUCCESS:
         raise TMSVRException('%s (data: %s)' % (res.errdesc, res.errdata))

   def set_value(self, key, value):
      return self.set_values({key: value})


if __name__ == "__main__":
   clnt = TMSVR_client(robot_ip='localhost', id='demo_client')
   try: clnt.set_value('Robot_Link', [3, 4])
   except TechmanException as e: print(type(e).__name__ + ': ' + str(e))
