#!/usr/bin/env python

import asyncio

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TMSTAException(TechmanException):
   pass

class TMSTA_client(TechmanClient):

   PORT=5890

   def __init__(self, *, robot_ip):
      super(TMSTA_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT)

   def is_listen_node_active(self):
      # Build TMSTA packet
      req = TMSTA_packet(TMSTA_type.IN_LISTEN_MODE, None)
      # Submit
      res = TMSTA_packet(self.send(req))
      # Parse response
      assert res.ptype == TMSTA_type.IN_LISTEN_MODE
      return res.params[0]

   def get_queue_tag_status(self, tag_id):
      # Build TMSTA packet
      req = TMSTA_packet(TMSTA_type.QUEUE_TAG, [tag_id])
      # Submit
      res = TMSTA_packet(self.send(req))
      # Parse response
      assert res.ptype == TMSTA_type.QUEUE_TAG
      return res.params[1]


if __name__ == "__main__":
   clnt = TMSTA_client(robot_ip='localhost')
   try: status = clnt.get_queue_tag_status(3)
   except TechmanException as e: print(type(e).__name__ + ': ' + str(e))
   print(f'Status: {status}')
