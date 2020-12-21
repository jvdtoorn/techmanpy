#!/usr/bin/env python

import ast

from techman_packet import TechmanPacket

class TMSCT_command_type:

   FUNCTION=0
   VARIABLE=1

class TMSCT_packet(TechmanPacket):

   def __init__(self, *args):
      if len(args) == 1:
         # Instantiated with TechmanPacket object
         if isinstance(args[0], TechmanPacket):
            self._header = args[0]._header
            self._data = args[0]._data
         # Instantiated with raw packet data
         else: super(TMSCT_packet, self).__init__(*args)
      # Instantiated with payload data
      elif len(args) == 2:
         self._header = 'TMSCT'
         self._data = self._encode_data(args[0], args[1])

   def _encode_data(self, handle_id, commands):
      commands = '\r\n'.join(commands)
      return '%s,%s' % (str(handle_id), commands)

   def _decode_data(self, data):
      handle_id = data[:data.find(',')]
      commands = data[data.find(',')+1:].split('\r\n')
      return handle_id, list(map(self._decode_command, commands))

   def _decode_command(self, command):
      if '(' not in command: return TMSCT_command_type.VARIABLE, command
      name = command[:command.find('(')]
      args = command[command.find('(')+1:command.find(')')].replace(' ', '')
      return TMSCT_command_type.FUNCTION, name, ast.literal_eval('[' + args + ']')

   @property
   def handle_id(self): return self._decode_data(self._data)[0]

   @property
   def commands(self): return self._decode_data(self._data)[1]


if __name__ == "__main__":
   msg = TMSCT_packet(3, ['ChangeBase("RobotBase")', 'ChangeLoad(10.1)', 'var_i = 1000', 'PTP(10, 10, 20, 30, 5)', 'PTP(10, [10, 20, 30], 5)'])
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.commands)
