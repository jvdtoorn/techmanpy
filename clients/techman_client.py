#!/usr/bin/env python

import asyncio

class TechmanClient:

   def __init__(self, *, robot_ip, robot_port, conn_timeout=3, suppress_warn=False):
      self._robot_ip = robot_ip
      self._robot_port = robot_port
      self._conn_timeout = conn_timeout
      self._suppress_warn = suppress_warn
      self._connection = None

   def _on_connection(self, reader, writer):
      return TechmanConnection(reader, writer, self._conn_timeout, self._suppress_warn)
   
   async def __aenter__(self):
      reader, writer = await asyncio.open_connection(self._robot_ip, self._robot_port)
      self._connection = self._on_connection(reader, writer)
      return self._connection

   async def __aexit__(self, exc_type, exc_msg, _): self._connection._close()

class TechmanConnection:

   def __init__(self, reader, writer, conn_timeout, suppress_warn):
      self._conn_timeout = conn_timeout
      self._suppress_warn = suppress_warn
      self._reader = reader
      self._writer = writer

   def _close(self): self._writer.close()
