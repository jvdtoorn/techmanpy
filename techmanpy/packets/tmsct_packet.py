#!/usr/bin/env python

import ast

from .stateful_packet import *
from ..exceptions import *

class TMSCT_type:

   REQUEST=0
   RESPONSE=1

class TMSCT_status:

   SUCCESS='OK'
   ERROR='ERROR'

class TMSCT_command_type:

   FUNCTION=0
   VARIABLE=1

class TMSCT_packet(StatefulPacket):

   HEADER='TMSCT'

   def __init__(self, *args):
      try:
         if len(args) == 1:
            # Instantiated with StatefulPacket object
            if isinstance(args[0], StatefulPacket):
               self._header = args[0]._header
               self._data = args[0]._data
            # Instantiated with raw packet data
            else: super().__init__(*args)
         # Instantiated with payload data
         else:
            self._header = self.HEADER
            self._data = self._encode_data(*args)
      except: raise TMParseError() from None

   def _encode_data(self, *args):
      encoded = super()._encode_data(args[0])
      ptype = args[1]
      if ptype == TMSCT_type.REQUEST:
         commands = '\r\n'.join(list(map(self._encode_command, args[2])))
         return encoded + commands
      if ptype == TMSCT_type.RESPONSE:
         if len(args[3]) == 0: return encoded + args[2]
         return encoded + f'{args[2]};{";".join(list(map(str, args[3])))}'

   def _decode_data(self, data):
      payload = data[data.find(',')+1:]
      status = TMSCT_status.SUCCESS if TMSCT_status.SUCCESS in payload else None
      if status is None: status = TMSCT_status.ERROR if TMSCT_status.ERROR in payload else None
      ptype = TMSCT_type.REQUEST if status is None else TMSCT_type.RESPONSE
      if ptype == TMSCT_type.REQUEST:
         commands = payload.split('\r\n')
         return ptype, list(map(self._decode_command, commands))
      else:
         parts = payload.split(';')
         lines = [] if len(parts) == 1 else list(map(int, parts[1:]))
         return ptype, status, lines

   def _encode_command(self, command):
      if len(command) == 2 and command[0] == TMSCT_command_type.VARIABLE: return command[1]
      name = command[0] if len(command) == 2 else command[1]
      arglist = command[1] if len(command) == 2 else command[2]
      argstr = str(arglist).replace(' ', '').replace('[', '{').replace(']', '}')
      argstr = argstr.replace('True', 'true').replace('False', 'false').replace('None', 'none')
      argstr = argstr.replace('\'', '"')
      return f'{name}({argstr[1:-1]})'

   def _decode_command(self, command):
      if '(' not in command: return TMSCT_command_type.VARIABLE, command
      name = command[:command.find('(')]
      args = command[command.find('(')+1:command.find(')')].replace(' ', '')
      args = args.replace('{', '[').replace('}', ']')
      args = args.replace('true', 'True').replace('false', 'False').replace('none', 'None')
      return TMSCT_command_type.FUNCTION, name, ast.literal_eval('[' + args + ']')

   @property
   def ptype(self): return self._decode_data(self._data)[0]

   @property
   def commands(self): return self._decode_data(self._data)[1]

   @property
   def status(self): return self._decode_data(self._data)[1]

   @property
   def lines(self): return self._decode_data(self._data)[2]
