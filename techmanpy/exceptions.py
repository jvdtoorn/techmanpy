#!/usr/bin/env python


class TechmanException(Exception):
   ''' Base class for exceptions. '''
   
   def __init__(self):
      super().__init__()
      self._msg = 'TechmanException: Something went wrong'

   def __str__(self): return str(self._msg).strip()

class TMConnectError(TechmanException):
   ''' Raised at connection related errors '''
   
   def __init__(self, exc, msg=None):
      super().__init__()
      if msg is not None: self._msg = f'TMConnectError: {msg}'
      else: self._msg = f'TMConnectError: {exc} ({type(exc).__name__})'

class TMParseError(TechmanException):
   ''' Raised at packet parse related errors '''

   def __init__(self):
      super().__init__()
      self._msg = 'TMParseError: Could not parse packet'

class TMProtocolError(TechmanException):
   ''' Raised at protocol related errors '''
   
   def __init__(self, msg):
      super().__init__()
      self._msg = f'TMProtocolError: {msg}'

class TMSTAError(TMProtocolError):
   ''' Raised at STA protocol related errors '''
   
   def __init__(self, msg):
      super().__init__(msg)
      self._msg = f'TMSTAError: {msg}'

class TMSVRError(TMProtocolError):
   ''' Raised at SVR protocol related errors '''
   
   def __init__(self, msg):
      super().__init__(msg)
      self._msg = f'TMSVRError: {msg}'

class TMSCTError(TMProtocolError):
   ''' Raised at SCT protocol related errors '''
   
   def __init__(self, msg):
      super().__init__(msg)
      self._msg = f'TMSCTError: {msg}'
