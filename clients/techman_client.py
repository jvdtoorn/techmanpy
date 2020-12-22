#!/usr/bin/env python

import asyncio
import threading
import time
from threading import Event
from kthread import KThread
import socket

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TechmanException(Exception):
   pass

class TechmanClient:

   def __init__(self, *, robot_ip, robot_port):
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._conn_exception = None
      self._loop = asyncio.get_event_loop()
      if not self._connect():
         print('[TechmanClient] WARN: Could not connect to robot during initialisation.')

   def _connect(self): return self._loop.run_until_complete(self._connect_async())
   async def _connect_async(self):
      try: 
         self._reader, self._writer = await asyncio.open_connection(self._robot_ip, self._robot_port)
      except Exception as e:
         self._conn_exception = e
         return False
      self._conn_exception = None
      return True

   @property
   def is_connected(self): return self._conn_exception is None
