#!/usr/bin/env python

import time

# Import library
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from clients.clients import *

ROBOT_IP='x.x.x.x'

if __name__ == "__main__":
   if 'x' in ROBOT_IP: print('Don\'t forget to specify the IP address of your robot!'); exit()
   while True:
      start = time.time()
      sct_connected, svr_connected, sta_connected = True, True, True

      # Check SCT connection (only active when inside listen node)
      try:
         client = TMSCT_client(robot_ip=ROBOT_IP, suppress_warn=True, conn_timeout=1)
         if not client.is_connected: raise TechmanException()
         client.resume_project()
      except TechmanException: sct_connected = False

      # Check SVR connection (should be always active)
      try:
         client = TMSVR_client(robot_ip=ROBOT_IP, suppress_warn=True, conn_timeout=1)
         if not client.is_connected: raise TechmanException()
         client.get_value('Robot_Model')
      except TechmanException: svr_connected = False

      # Check STA connection (only active when running project)
      try:
         client = TMSTA_client(robot_ip=ROBOT_IP, suppress_warn=True, conn_timeout=1)
         if not client.is_connected: raise TechmanException()
         client.is_listen_node_active()
      except TechmanException: sta_connected = False

      # Print status
      online, offline = [], []
      online.append('SCT') if sct_connected else offline.append('SCT')
      online.append('SVR') if svr_connected else offline.append('SVR')
      online.append('STA') if sta_connected else offline.append('STA')
      print(f'online protocols: {online}, offline protocols: {offline}')

      # Sleep 2 seconds (at most)
      elapsed = time.time() - start
      if elapsed < 2: time.sleep(2 - elapsed)
