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

   def __init__(self, broadcast_callback=None, *, robot_ip, id):
      super(TMSVR_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT)
      self._broadcast_callback = broadcast_callback
      self._id = str(id)
      self._msg_cnt = 0

   def _handle_incoming(self, packet):
      packet = TMSVR_packet(packet)
      if len(packet.handle_id) == 1:
         self._broadcast_callback(packet)
         return
      index = -1
      callback = None
      for i, request in enumerate(self._outgoing_requests):
         if request[0] != packet.handle_id: continue
         index = i
         callback = request[1]
      assert index != -1
      del self._outgoing_requests[index]
      # Execute callback with received packet
      callback(packet)

   def _handle_outgoing(self, packet, callback):
      self._outgoing_requests.append((packet.handle_id, callback))

   def get_values(self, items):
      # Build TMSVR packet
      handle_id = '%s%d' % (self._id, self._msg_cnt)
      self._msg_cnt += 1
      req = TMSVR_packet(handle_id, TMSVR_type.READ_REQUEST, items)
      # Submit
      res = TMSVR_packet(self.send(req))
      print(res.encoded())
      # Parse response
      assert res.handle_id == handle_id
      print(req.ptype)
      print(res.ptype)
      print(TMSVR_type.READ_RESPONSE)
      assert res.ptype == TMSVR_type.READ_RESPONSE
      return res.items

   def get_value(self, key):
      return self.get_values({key})

   def set_values(self, items):
      # Build TMSVR packet
      handle_id = '%s%d' % (self._id, self._msg_cnt)
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
   def broadcast_callback(packet):
      print(f'Received {packet._header} packet with id {packet.handle_id}')
      #print('blokkie nee')
      #print(packet.items)
      #print('blokkie huh')
   clnt = TMSVR_client(robot_ip='10.66.0.117', id='DC', broadcast_callback=broadcast_callback)
   #try:
      #clnt.set_value('Camera_Light', 0)
      # print(clnt.get_value('Camera_Light'))
   #except TechmanException as e: print(type(e).__name__ + ': ' + str(e))

   asyncio.get_event_loop().run_forever()
   print('nee toch')