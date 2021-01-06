#!/usr/bin/env python

from .stateless_packet import *
from ..exceptions import *

class CPERR_code:

   SUCCESS=0x00
   PACKET_ERR=0x01
   CHECKSUM_ERR=0x02
   HEADER_ERR=0x03
   DATA_ERR=0x04
   NO_LISTEN=0xF1

   @staticmethod
   def description(value):
      if value == CPERR_code.SUCCESS: return 'Success'
      if value == CPERR_code.PACKET_ERR: return 'Packet error'
      if value == CPERR_code.CHECKSUM_ERR: return 'Checksum error'
      if value == CPERR_code.HEADER_ERR: return 'Header error'
      if value == CPERR_code.DATA_ERR: return 'Packet data error'
      if value == CPERR_code.NO_LISTEN: return 'Listen Node is not active'
      return 'Unknown error'

class CPERR_packet(StatelessPacket):

   HEADER='CPERR'

   def __init__(self, *args):
      try:
         # Instantiated with StatelessPacket object
         if isinstance(args[0], StatelessPacket):
            self._header = args[0]._header
            self._data = args[0]._data
         # Instantiated with raw packet data
         elif not isinstance(args[0], int): super().__init__(*args)
         # Instantiated with payload data
         else:
            self._header = self.HEADER
            self._data = self._encode_data(args[0])
      except: raise TMParseError() from None

   def _encode_data(self, error_code):
      return f'{error_code:02X}'

   def _decode_data(self, data):
      return int(data, 16)

   @property
   def value(self): return self._decode_data(self._data)

   @property
   def description(self): return CPERR_code.description(self.value)
