#!/usr/bin/env python

import sys

from ..exceptions import *

class StatelessPacket:

   def __init__(self, *args):
      try:
         self._header, self._data = None, None
         if len(args) == 1:
            self._header, self._data = self._decode(args[0])
         elif len(args) == 2:
            self._header = args[0]
            self._data = args[1]
      except: raise TMParseError() from None

   def _encode(self, header, data):
      checksum_data = f'{header},{len(data)},{data},'
      checksum = 0b0
      utf_str = checksum_data.encode('utf-8')
      for byte in utf_str: checksum ^= byte
      return f'${checksum_data}*{checksum:02X}\r\n'

   def _decode(self, packet):
      if isinstance(packet, bytes): packet = packet.decode('utf-8')
      header = packet[1:self._find_nth(packet, ',', 1)]
      data_length = int(packet[self._find_nth(packet, ',', 1)+1:self._find_nth(packet, ',', 2)])
      data = packet[self._find_nth(packet, ',', 2)+1:self._find_nth(packet, ',', 2)+1+data_length]
      return header, data

   def _find_nth(self, msg, pattern, n):
      start = msg.find(pattern)
      while start >= 0 and n > 1:
         start = msg.find(pattern, start+len(pattern))
         n -= 1
      return start

   def encoded(self): return self._encode(self._header, self._data).encode('utf-8')
