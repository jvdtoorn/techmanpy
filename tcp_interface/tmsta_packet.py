#!/usr/bin/env python

from techman_packet import TechmanPacket

class TMSTA_packet(TechmanPacket):

   LISTEN_MODE=0
   QUEUE=1

   def __init__(self, *args):
      if len(args) == 1: super(TMSTA_packet, self).__init__(args)
      elif len(args) == 2:
         self._header = 'TMSTA'
         self._data = self._encode_data(args[0], args[1])

   def _encode_data(self, mode, params):
      if isinstance(mode, int): mode = self._encode_int(mode)
      if params is None: return '%s' % mode
      params = ','.join(list(map(self._encode_param, params)))
      return '%s,%s' % (mode, params)

   def _decode_data(self, data):
      if ',' not in data: return self._decode_int(data), None
      mode = self._decode_int(data[:data.find(',')])
      params = data[data.find(',')+1:].split(',')
      return mode, list(map(self._decode_param, params))

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
   def mode(self): return self._decode_data(self._data)[0]

   @property
   def params(self): return self._decode_data(self._data)[1]


if __name__ == "__main__":
   msg = TMSTA_packet(TMSTA_packet.QUEUE, [None])
   print(msg.encoded())
   print(msg.mode)
   print(msg.params)
