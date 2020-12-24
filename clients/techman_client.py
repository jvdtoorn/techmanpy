#!/usr/bin/env python

import asyncio

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from util.exceptions import * # pylint: disable=no-name-in-module

class TechmanClient:

   def __init__(self, *, robot_ip, robot_port, conn_timeout=3):
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._conn_timeout = conn_timeout
      self._connection = None

   def _on_connection(self, reader, writer):
      return TechmanConnection(reader, writer, self._conn_timeout)
   
   async def __aenter__(self):
      try:
         reader, writer = await asyncio.open_connection(self._robot_ip, self._robot_port)
         self._connection = self._on_connection(reader, writer)
         return self._connection
      except ConnectionError as e: raise TMConnectError(e)

   async def __aexit__(self, exc_type, exc_msg, _): self._connection._close()

class TechmanConnection:

   def __init__(self, reader, writer, conn_timeout):
      self._conn_timeout = conn_timeout
      self._reader = reader
      self._writer = writer

   def _close(self): self._writer.close()
