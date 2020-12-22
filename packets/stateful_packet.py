#!/usr/bin/env python

import sys

from stateless_packet import StatelessPacket

class StatefulPacket(StatelessPacket):

   def __init__(self, *args):
      super(StatefulPacket, self).__init__(*args)

   def _encode_data(self, handle_id):
      return '%s,' % str(handle_id)

   @property
   def handle_id(self):
      return self._data[:self._data.find(',')]
