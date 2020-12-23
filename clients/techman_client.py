#!/usr/bin/env python

import asyncio

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TechmanException(Exception):
   pass

class TechmanClient(object):

   # Allow async object creation
   async def __new__(cls, *a, **kw):
      instance = super().__new__(cls)
      await instance.__init__(*a, **kw) # pylint: disable=missing-kwoa
      return instance

   async def __init__(self, suppress_warn=False, conn_timeout=3, *, robot_ip, robot_port):
      self._conn_timeout = conn_timeout
      self._suppress_warn = suppress_warn
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._conn_exception = None
      self._loop = asyncio.get_event_loop()
      if not await self._connect_async():
         if not self._suppress_warn: print('[TechmanClient] WARN: Could not connect to robot during initialisation.')

   async def _connect_async(self):
      connect_fut = asyncio.open_connection(self._robot_ip, self._robot_port)
      try: 
         self._reader, self._writer = await asyncio.wait_for(connect_fut, timeout=self._conn_timeout)
      except RuntimeError as e:
         if 'coroutine' in str(e): raise TechmanException('Only one client creation can be active at any time!') from None
         else: raise e
      except Exception as e:
         self._conn_exception = e
         return False
      self._conn_exception = None
      return True

   @property
   def is_connected(self): return self._conn_exception is None

   def __del__(self):
      try:
         # If event loop is still open, close the socket reader and writer
         asyncio.get_event_loop()
         if hasattr(self, '_reader'): self._reader.close()
         if hasattr(self, '_writer'): self._writer.close()
      except: pass
