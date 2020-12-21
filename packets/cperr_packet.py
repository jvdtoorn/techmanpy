#!/usr/bin/env python

from techman_packet import TechmanPacket

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

class CPERR_packet(TechmanPacket):

   def __init__(self, *args):
      # Instantiated with TechmanPacket object
      if isinstance(args[0], TechmanPacket):
         self._header = args[0]._header
         self._data = args[0]._data
      # Instantiated with raw packet data
      elif not isinstance(args[0], int): super(CPERR_packet, self).__init__(*args)
      # Instantiated with payload data
      else:
         self._header = 'CPERR'
         self._data = self._encode_data(args[0])

   def _encode_data(self, error_code):
      return '{:02x}'.format(error_code).upper()

   def _decode_data(self, data):
      return int(data, 16)

   @property
   def value(self): return self._decode_data(self._data)

   @property
   def description(self): return CPERR_code.description(self.value)


if __name__ == "__main__":
   error = CPERR_packet(CPERR_code.NO_LISTEN)
   print(error.encoded())
   print(error.value)
   print(error.description)