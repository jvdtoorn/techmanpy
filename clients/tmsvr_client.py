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
         if self._broadcast_callback is not None: self._broadcast_callback(packet)
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

import logging
import signal

clnt = None

def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    #msg = context.get(context['message'])
    logging.error(f"Caught exception: {msg}")
    logging.info("Shutting down (not)...")
    #asyncio.get_event_loop().create_task(shutdown(loop))

async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logging.info(f"Received exit signal {signal.name}...")
    # tasks = [t for t in asyncio.get_event_loop().all_tasks() if t is not
             #asyncio.get_event_loop().current_task()]

    #[task.cancel() for task in asyncio.all_tasks()]

    #logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    print('waitin')
    clnt._listen_task.cancel()
    #await asyncio.gather(clnt._listen_task, return_exceptions=True)
    print('nop')
    logging.info(f"Flushing metrics")
    loop.stop()

if __name__ == "__main__":

   clnt = TMSVR_client(robot_ip='10.66.0.117', id='DC')
   try: clnt.set_value('Camera_Light', 0) # could do more than 1 read if SVR intervenes
   except: print('too bad')

   # exit

   print('2')
   print('value: ' + str(clnt.get_value('Camera_Light')))
   print('hallo?')
   asyncio.get_event_loop().run_until_complete(clnt._listen_task)
   exit()

   logging.basicConfig(
      level=logging.DEBUG,
      format="%(asctime)s [%(levelname)s] %(message)s"
   )

   loop = asyncio.get_event_loop()
   # May want to catch other signals too
   signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
   for s in signals:
      loop.add_signal_handler(
         s, lambda s=s: loop.create_task(shutdown(loop, signal=s)))
   loop.set_exception_handler(handle_exception)

   def broadcast_callback(packet):
      # pass
      print(f'Received {packet._header} packet with id {packet.handle_id}')
      #val = packet.items['System_Uptime']
      # print(val)
      #print('blokkie nee')
      #print(packet.items)
      #print('blokkie huh')
   
   clnt = TMSVR_client(robot_ip='10.66.0.117', id='DC') #, broadcast_callback=broadcast_callback)
   print('1')
   clnt.set_value('Camera_Light', 0)
   print('2')
   print(clnt.get_value('Camera_Light'))
   print('hallo?')
   asyncio.get_event_loop().run_forever()
   # try:
   #    clnt.set_value('Camera_Light', 0)
   #    print('priem')
   #    print(clnt.get_value('Camera_Light'))
   # except TechmanException as e: print(type(e).__name__ + ': ' + str(e))