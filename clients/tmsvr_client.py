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
      super(TMSVR_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT, broadcast_callback=broadcast_callback)
      self._id = str(id)
      self._msg_cnt = 0

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
      print(req.encoded())
      # Submit
      res = TMSVR_packet(self.send(req))
      # Parse response
      print(res.handle_id)
      print(handle_id)
      assert res.handle_id == handle_id
      assert res.ptype == TMSVR_type.WRITE_RESPONSE
      if res.status != TMSVR_status.SUCCESS:
         raise TMSVRException('%s (data: %s)' % (res.errdesc, res.errdata))

   def set_value(self, key, value):
      return self.set_values({key: value})

   def listen(self): return asyncio.get_event_loop().run_until_complete(self._listen_async())
   async def _listen_async(self):
      if not self._is_connected:
         if await self._connect_async(): self._is_connected = True
         else: raise TechmanException('Could not connect to robot at %s:%s' % (self._robot_ip, self._robot_port))
      read_bytes = await self._reader.read(1024)
      if read_bytes == b'':
         if self._reconnect_cnt > 5:
            self._reconnect_cnt = 0
            raise TechmanException('Could not connect to robot at %s:%s' % (self._robot_ip, self._robot_port))
         self._reconnect_cnt += 1
         self._is_connected = False
         return await self._send_async(techman_packet)
      else: 
         self._reconnect_cnt = 0
         res = TechmanPacket(read_bytes)
         if res._header == 'CPERR':
            raise TechmanException(CPERR_packet(res).description)
         else: return res


if __name__ == "__main__":
   def broadcast_callback(packet):
      print(f'Received {packet._header} packet')
   clnt = TMSVR_client(robot_ip='10.66.0.117', id='DC', broadcast_callback=broadcast_callback)
   try:
      print(clnt.listen().encoded())
      clnt.set_value('Camera_Light', 1)
      # print(clnt.get_value('Camera_Light'))
   except TechmanException as e: print(type(e).__name__ + ': ' + str(e))
