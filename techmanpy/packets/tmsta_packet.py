#!/usr/bin/env python

from .stateless_packet import *
from ..exceptions import *

class TMSTA_type:

   IN_LISTEN_MODE=0
   QUEUE_TAG=1

class TMSTA_packet(StatelessPacket):

   HEADER='TMSTA'

   def __init__(self, *args):
      try:
         if len(args) == 1:
            # Instantiated with StatelessPacket object
            if isinstance(args[0], StatelessPacket):
               self._header = args[0]._header
               self._data = args[0]._data
            # Instantiated with raw packet data
            else: super().__init__(*args)
         # Instantiated with payload data
         elif len(args) == 2:
            self._header = self.HEADER
            self._data = self._encode_data(args[0], args[1])
      except: raise TMParseError() from None

   def _encode_data(self, ptype, params):
      if isinstance(ptype, int): ptype = self._encode_int(ptype)
      if params is None: return f'{ptype}'
      params = ','.join(list(map(self._encode_param, params)))
      return f'{ptype},{params}'

   def _decode_data(self, data):
      if ',' not in data: return self._decode_int(data), None
      ptype = self._decode_int(data[:data.find(',')])
      params = data[data.find(',')+1:].split(',')
      return ptype, list(map(self._decode_param, params))

   def _encode_param(self, param):
      if param is None: return 'none'
      if isinstance(param, bool) and param == True: return 'true'
      if isinstance(param, bool) and param == False: return 'false'
      if isinstance(param, int): return self._encode_int(param)
      return param

   def _decode_param(self, param):
      if param == 'none': return None
      if param == 'true': return True
      if param == 'false': return False
      if len(param) == 0: return param
      if param[0] == '0' or param[0] == '1': return self._decode_int(param)
      return param

   def _encode_int(self, value):
      if value >= 10: return str(value)
      else: return '0' + str(value)

   def _decode_int(self, str):
      if str[0] == '0': return int(str[1])
      else: return int(str)

   @property
   def ptype(self): return self._decode_data(self._data)[0]

   @property
   def params(self): return self._decode_data(self._data)[1]
