#!/usr/bin/env python

import ast

from .stateful_packet import *
from ..exceptions import *

class TMSVR_type:

   RESPONSE_STATUS=0
   VALUE_DATA=2
   VALUE_REQUEST=12

class TMSVR_status:

   SUCCESS=(0x00, 'OK')
   FORMAT_ERROR=(0x01, 'NotSupport')
   IP_NO_WRITE=(0x02, 'WritePermission')
   FORMAT_MISMATCH=(0x03, 'InvalidData')
   ITEM_NOEXIST=(0x04, 'NotExist')
   WRITE_PROTECTED=(0x05, 'ReadOnly')
   MODE_PROTECTED=(0x06, 'ModeError')
   VARTYPE_MISMATCH=(0x07, 'ValueError')

   @staticmethod
   def value(value):
      if value == TMSVR_status.SUCCESS[0]: return TMSVR_status.SUCCESS
      if value == TMSVR_status.FORMAT_ERROR[0]: return TMSVR_status.FORMAT_ERROR
      if value == TMSVR_status.IP_NO_WRITE[0]: return TMSVR_status.IP_NO_WRITE
      if value == TMSVR_status.FORMAT_MISMATCH[0]: return TMSVR_status.FORMAT_MISMATCH
      if value == TMSVR_status.ITEM_NOEXIST[0]: return TMSVR_status.ITEM_NOEXIST
      if value == TMSVR_status.WRITE_PROTECTED[0]: return TMSVR_status.WRITE_PROTECTED
      if value == TMSVR_status.MODE_PROTECTED[0]: return TMSVR_status.MODE_PROTECTED
      if value == TMSVR_status.VARTYPE_MISMATCH[0]: return TMSVR_status.VARTYPE_MISMATCH

   @staticmethod
   def description(status):
      if status == TMSVR_status.SUCCESS: return 'Success'
      if status == TMSVR_status.FORMAT_ERROR: return 'The communication format or mode is not supported'
      if status == TMSVR_status.IP_NO_WRITE: return 'The connected client is not permitted to write'
      if status == TMSVR_status.FORMAT_MISMATCH: return 'The communication format and the data content format are mismatched'
      if status == TMSVR_status.ITEM_NOEXIST: return 'Item to write or read does not exist'
      if status == TMSVR_status.WRITE_PROTECTED: return 'Unable to write to read-only items'
      if status == TMSVR_status.MODE_PROTECTED: return 'Can\'t write in the current control mode, try switching to auto mode'
      if status == TMSVR_status.VARTYPE_MISMATCH: return 'Values to write mismatches with the configured type or the size.'

class TMSVR_packet(StatefulPacket):

   HEADER='TMSVR'

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
      encoded += f'{ptype},'
      if ptype == TMSVR_type.VALUE_REQUEST:
         for variable in args[2]:
            encoded += f'{variable}\r\n'
         encoded = encoded[:len(encoded)-2]
      elif ptype == TMSVR_type.VALUE_DATA:
         for variable, value in args[2].items():
            encoded += f'{variable}={self._encode_value(value)}\r\n'
         encoded = encoded[:len(encoded)-2]
      elif ptype == TMSVR_type.RESPONSE_STATUS:
         encoded += f'{args[2][0]:02X},'
         if len(args) == 3: encoded += args[2][1]
         else: encoded += f'{args[2][1]};{args[3]}'
      return encoded

   def _decode_data(self, data):
      ptype = int(data[self._find_nth(data, ',', 1)+1:self._find_nth(data, ',', 2)])
      payload = data[self._find_nth(data, ',', 2)+1:]
      # Correct protocol bug
      if ptype == TMSVR_type.VALUE_REQUEST and '=' in payload: ptype = TMSVR_type.VALUE_DATA
      # Decode payload based on packet type
      if ptype == TMSVR_type.VALUE_REQUEST:
         return ptype, set(payload.split('\r\n'))
      if ptype == TMSVR_type.VALUE_DATA:
         items = {}
         for varval in payload.split('\r\n'):
            var, val = varval.split('=')
            items[var] = self._decode_value(val)
         return ptype, items
      if ptype == TMSVR_type.RESPONSE_STATUS:
         status = TMSVR_status.value(int(payload[:payload.find(',')], 16))
         errdata = None if ';' not in payload else payload[payload.find(';')+1:]
         return ptype, status, errdata

   def _encode_value(self, value):
      if isinstance(value, str): return f'"{value}"'
      if isinstance(value, list):
         return str(value).replace(' ', '').replace('[', '{').replace(']', '}')
      if isinstance(value, bool) and value == True: return 'true'
      if isinstance(value, bool) and value == False: return 'false'
      return str(value)

   def _decode_value(self, value):
      if value == 'true': return True
      if value == 'false': return False
      if '"' in value: return value[1:len(value)-1]
      if '{' in value: return ast.literal_eval(value.replace('{', '[').replace('}', ']'))
      return ast.literal_eval(value)

   @property
   def ptype(self): return self._decode_data(self._data)[0]

   @property
   def status(self): return self._decode_data(self._data)[1]

   @property
   def errdata(self): return self._decode_data(self._data)[2]

   @property
   def errdesc(self): return TMSVR_status.description(self.status)

   @property
   def items(self): return self._decode_data(self._data)[1]
