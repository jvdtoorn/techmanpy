#!/usr/bin/env python

import asyncio

from ..exceptions import *

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
      except ConnectionError as e: raise TMConnectError(e) from None

   async def __aexit__(self, exc_type, exc_msg, _): self._connection._close()

class TechmanConnection:

   def __init__(self, reader, writer, conn_timeout):
      self._conn_timeout = conn_timeout
      self._reader = reader
      self._writer = writer
      self._init_vars()
   
   def _init_vars(self): pass

   def _close(self): self._writer.close()
