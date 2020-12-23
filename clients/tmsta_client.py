#!/usr/bin/env python

import asyncio

from stateless_client import StatelessClient
from techman_client import TechmanException

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TMSTAException(TechmanException):
   pass

class TMSTA_client(StatelessClient):

   PORT=5890

   def __init__(self, suppress_warn=False, conn_timeout=None, *, robot_ip):
      super(TMSTA_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT, conn_timeout=conn_timeout, suppress_warn=suppress_warn)

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
