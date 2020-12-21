#!/usr/bin/env python

import ast

from techman_packet import TechmanPacket

# NOTE: Make sure that the Ethernet Slave format is set to 'string'

class TMSVR_type:

   READ_REQUEST=12
   READ_RESPONSE=2
   WRITE_REQUEST=2
   WRITE_RESPONSE=0

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

class TMSVR_packet(TechmanPacket):

   def __init__(self, *args):
      if len(args) == 1:
         # Instantiated with TechmanPacket object
         if isinstance(args[0], TechmanPacket):
            self._header = args[0]._header
            self._data = args[0]._data
         # Instantiated with raw packet data
         else: super(TMSVR_packet, self).__init__(*args)
      # Instantiated with payload data
      else:
         self._header = 'TMSVR'
         self._data = self._encode_data(*args)

   def _encode_data(self, *args):
      handle_id = args[0]
      ptype = args[1]
      encoded = '%s,%s,' % (handle_id, ptype)
      if ptype == TMSVR_type.READ_REQUEST:
         for variable in args[2]:
            encoded += '%s\r\n' % variable
         encoded = encoded[:len(encoded)-2]
      elif ptype == TMSVR_type.WRITE_REQUEST: # same as TMSVR_type.READ_RESPONSE
         for variable, value in args[2].items():
            encoded += '%s=%s\r\n' % (variable, self._encode_value(value))
         encoded = encoded[:len(encoded)-2]
      elif ptype == TMSVR_type.WRITE_RESPONSE:
         encoded += '%s,' % '{:02x}'.format(args[2][0]).upper()
         if args[3] is None: encoded += args[2][1]
         else: encoded += '%s;%s' % (args[2][1], args[3])
      return encoded

   def _decode_data(self, data):
      handle_id = data[:data.find(',')]
      ptype = int(data[self._find_nth(data, ',', 1)+1:self._find_nth(data, ',', 2)])
      payload = data[self._find_nth(data, ',', 2)+1:]
      if ptype == TMSVR_type.READ_REQUEST:
         return handle_id, ptype, set(payload.split('\r\n'))
      if ptype == TMSVR_type.WRITE_REQUEST: # same as TMSVR_type.READ_RESPONSE
         items = {}
         for varval in payload.split('\r\n'):
            var, val = varval.split('=')
            items[var] = self._decode_value(val)
         return handle_id, ptype, items
      if ptype == TMSVR_type.WRITE_RESPONSE:
         status = TMSVR_status.value(int(payload[:payload.find(',')], 16))
         errdata = None if ';' not in payload else payload[payload.find(';')+1:]
         return handle_id, ptype, status, errdata

   def _encode_value(self, value):
      if isinstance(value, str): return '"%s"' % value
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
   def handle_id(self): return self._decode_data(self._data)[0]

   @property
   def ptype(self): return self._decode_data(self._data)[1]

   @property
   def status(self): return self._decode_data(self._data)[2]

   @property
   def errdata(self): return self._decode_data(self._data)[3]

   @property
   def errdesc(self): return TMSVR_status.description(self.status)

   @property
   def items(self): return self._decode_data(self._data)[2]


if __name__ == "__main__":
   msg = TMSVR_packet('S1', TMSVR_type.WRITE_RESPONSE, TMSVR_status.FORMAT_ERROR, None)
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.ptype)
   print(msg.status)
   print(msg.errdata)

   msg = TMSVR_packet('S5', TMSVR_type.WRITE_RESPONSE, TMSVR_status.WRITE_PROTECTED, 'Robot_Link')
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.ptype)
   print(msg.status)
   print(msg.errdata)

   msg = TMSVR_packet('S4', TMSVR_type.WRITE_REQUEST, {'Ctrl_DO32': 1})
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.ptype)
   print(msg.items)

   msg = TMSVR_packet('Q2', TMSVR_type.READ_REQUEST, {'Robot_Link', 'TCP_Mass'})
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.ptype)
   print(msg.items)

   msg = TMSVR_packet('S7', TMSVR_type.WRITE_REQUEST, {'adata': [1, 2, 3]})
   print(msg.encoded())
   print(msg.handle_id)
   print(msg.ptype)
   print(msg.items)