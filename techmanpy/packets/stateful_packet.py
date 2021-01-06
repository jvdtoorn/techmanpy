#!/usr/bin/env python

import sys

from .stateless_packet import *
from ..exceptions import *

class StatefulPacket(StatelessPacket):

   def __init__(self, *args):
      try: super().__init__(*args)
      except: raise TMParseError() from None

   def _encode_data(self, handle_id):
      return f'{handle_id},'

   @property
   def handle_id(self):
      return self._data[:self._data.find(',')]
