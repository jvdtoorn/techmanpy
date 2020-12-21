#!/usr/bin/env python

import asyncio

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TechmanClient:

   def __init__(self, *, robot_ip, robot_port):
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._is_connected = self._connect()
      self._reconnect_cnt = 0
      if not self._is_connected:
         print('[TechmanClient] WARN: Not connected to robot yet. Will try again when sending message.')

   def _connect(self): return asyncio.get_event_loop().run_until_complete(self._connect_async())
   async def _connect_async(self):
      try: self._reader, self._writer = await asyncio.open_connection(self._robot_ip, self._robot_port)
      except ConnectionError: return False
      return True

   def send(self, techman_packet): return asyncio.get_event_loop().run_until_complete(self._send_async(techman_packet))
   async def _send_async(self, techman_packet):
      if not self._is_connected:
         if await self._connect_async(): self._is_connected = True
         else: raise ConnectionError('[TechmanClient] ERROR: Could not connect to robot')
      self._writer.write(techman_packet.encoded())
      read_bytes = await self._reader.read(1024)
      if read_bytes == b'':
         if self._reconnect_cnt > 5:
            self._reconnect_cnt = 0
            raise ConnectionError('[TechmanClient] ERROR: Could not connect to robot')
         self._reconnect_cnt += 1
         self._is_connected = False
         return await self._send_async(techman_packet)
      else: 
         self._reconnect_cnt = 0
         return TechmanPacket(read_bytes)

   def __del__(self):
      if hasattr(self, '_writer'):
         self._writer.close()      
      asyncio.get_event_loop().close()
