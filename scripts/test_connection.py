#!/usr/bin/env python

import asyncio
import time

# Import library
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from clients.clients import *
from util.exceptions import *

async def test_connection(robot_ip):
   while True:
      start = time.time()
      status = {'SCT': 'offline', 'SVR': 'offline', 'STA': 'offline'}

      # Check SVR connection (should be always active)
      try:
         async with TMSVR_client(robot_ip=robot_ip, conn_timeout=1) as conn:
            status['SVR'] = 'online'
            await conn.get_value('Robot_Model')
            status['SVR'] = 'connected'
      except TechmanException: pass

      # Check SCT connection (only active when inside listen node)
      try:
         async with TMSCT_client(robot_ip=robot_ip, conn_timeout=1) as conn:
            status['SCT'] = 'online'
            await conn.resume_project()
            status['SCT'] = 'connected'
      except TechmanException: pass

      # Check STA connection (only active when running project)
      try:
         async with TMSTA_client(robot_ip=robot_ip, conn_timeout=1) as conn:
            status['STA'] = 'online'
            await conn.is_listen_node_active()
            status['STA'] = 'connected'
      except TechmanException: pass

      # Print status
      def colored(status):
         if status == 'online': return f'\033[96m{status}\033[00m'
         if status == 'connected': return f'\033[92m{status}\033[00m'
         if status == 'offline': return f'\033[91m{status}\033[00m'
      print(f'SVR: {colored(status["SVR"])}, SCT: {colored(status["SCT"])}, STA: {colored(status["STA"])}')

      # Sleep 2 seconds (at most)
      elapsed = time.time() - start
      if elapsed < 2: time.sleep(2 - elapsed)

if __name__ == '__main__':
   if len(sys.argv) == 2: asyncio.run(test_connection(sys.argv[1]))
   else: print(f'usage: {sys.argv[0]} <robot IP address>')
