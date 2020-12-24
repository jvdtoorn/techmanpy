#!/usr/bin/env python

import sys

from stateless_packet import StatelessPacket

# Import 'util' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from util.exceptions import * # pylint: disable=no-name-in-module

class StatefulPacket(StatelessPacket):

   def __init__(self, *args):
      try: super().__init__(*args)
      except: raise TMParseError()

   def _encode_data(self, handle_id):
      return f'{handle_id},'

   @property
   def handle_id(self):
      return self._data[:self._data.find(',')]
