#!/usr/bin/env python

import sys

class TechmanPacket:

   def __init__(self, *args):
      self._header, self._data = None, None
      if len(args) == 1:
         self._header, self._data = self._decode(args[0])
      elif len(args) == 2:
         self._header = args[0]
         self._data = args[1]

   def _encode(self, header, data):
      checksum_data = '%s,%d,%s,' % (header, len(data), data)
      checksum = 0b0
      utf_str = checksum_data.encode('utf-8')
      if sys.version_info[0] < 3: ba = bytearray(); ba.extend(utf_str); utf_str = ba
      for byte in utf_str: checksum ^= byte
      return '$%s*%s\r\n' % (checksum_data, '{:02x}'.format(checksum).upper())

   def _decode(self, packet):
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

   def encoded(self): return self._encode(self._header, self._data)
