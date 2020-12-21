#!/usr/bin/env python

import asyncio

from techman_client import TechmanException, TechmanClient

# Import 'packets' folder
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path: sys.path.insert(0, parentdir)
from packets.packets import *

class TMSCTException(TechmanException):
   pass

class TMSCT_client(TechmanClient):

   # Durations are in milliseconds
   # Sizes are in millimeters
   # Angles are in degrees
   # Percentages are a float between 0.0 and 1.0

   # TODO: Add support for return values
   # TODO: Probably have to expand arrays to individual args

   PORT=5890

   def __init__(self, *, robot_ip, id):
      super(TMSCT_client, self).__init__(robot_ip=robot_ip, robot_port=self.PORT)
      self._id = str(id)
      self.g_cnt = 0
      self._in_transaction = False
      self._transaction = []

   def _execute_commands(self, commands):
      # Build TMSCT packet
      handle_id = '%s_%d' % (self._id, self.g_cnt)
      self.g_cnt += 1
      req = TMSCT_packet(handle_id, TMSCT_type.REQUEST, commands)
      # Submit
      res = TMSCT_packet(self.send(req))
      # Parse response
      assert res.handle_id == handle_id
      assert res.ptype == TMSCT_type.RESPONSE
      if len(res.lines) > 0:
         commands = [res.commands[i] for i in res.lines]
         enc_cmnds = list(map(req._encode_command, commands))
         if res.status == TMSCT_status.SUCCESS:
            if len(res.lines) == 1:
               print('[TMSCT_client] WARN: The command \'%s\' resulted in a warning' % enc_cmnds[0])
            else: print('[TMSCT_client] WARN: The following commands resulted in a warning: %s' % enc_cmnds)
         if res.status == TMSCT_status.ERROR:
            if len(res.lines) == 1: raise TMSCTException('The command \'%s\' resulted in an error' % enc_cmnds[0])
            else: raise TMSCTException('The following commands resulted in an error: %s' % enc_cmnds)

   def _execute_command(self, command):
      if self._in_transaction: self._transaction.append(command)
      else: return self._execute_commands([command])

   def start_transaction(self):
      self._in_transaction = True

   def submit_transaction(self):
      transaction = self._transaction
      self._transaction = None
      self._in_transaction = False
      return self._execute_commands(transaction)

   # ==== general commmands ====

   def set_queue_tag(self, tag_id, wait_for_completion=False):
      return self._execute_command(('QueueTag', [tag_id, 1 if wait_for_completion else 0]))

   def wait_for_queue_tag(self, tag_id, timeout=-1):
      return self._execute_command(('WaitQueueTag', [tag_id, int(timeout)]))

   def stop_motion(self):
      return self._execute_command(('StopAndClearBuffer', []))

   def pause_project(self):
      return self._execute_command(('Pause', []))

   def resume_project(self):
      return self._execute_command(('Resume', []))

   # NOTE: 'base' argument can be either config name (string) or coordinate frame 
   def set_base(self, base):
      return self._execute_command(('ChangeBase', [base]))

   # NOTE: 'tcp' argument can be either config name (string) or coordinate frame 
   def set_tcp(self, tcp, weight=None, inertia=None):
      arglist = [tcp]
      if weight is not None: arglist.append(weight)
      if inertia is not None: arglist.append(inertia)
      return self._execute_command(('ChangeTCP', arglist))

   def set_load_weight(self, weight):
      return self._execute_command(('ChangeLoad', [weight]))

   def enter_point_pvt_mode(self):
      return self._execute_command(('PVTEnter', [1]))

   def add_pvt_point(self, tcp_point_goal, tcp_point_velocities_goal, duration):
      return self._execute_command(('PVTPoint', [tcp_point_goal, tcp_point_velocities_goal, duration/1000.0]))

   def enter_joint_pvt_mode(self):
      return self._execute_command(('PVTEnter', [0]))

   def add_pvt_joint_angles(self, joint_angles_goal, joint_angle_velocities_goal, duration):
      return self._execute_command(('PVTPoint', [joint_angles_goal, joint_angle_velocities_goal, duration/1000.0]))

   def exit_pvt_mode(self):
      return self._execute_command(('PVTExit', []))

   def pause_pvt_mode(self):
      return self._execute_command(('PVTPause', []))

   def resume_pvt_mode(self):
      return self._execute_command(('PVTResume', []))

   # ==== PTP ====

   def move_to_point_ptp(self, tcp_point_goal, speed_perc, acceleration_duration, blending_perc, use_precise_positioning=False, pose_goal=None):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      arglist = ['CPP', tcp_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]
      if pose_goal is not None: arglist.append(pose_goal)
      return self._execute_command(('PTP', arglist))

   def move_to_relative_point_ptp(self, relative_point_goal, speed_perc, acceleration_duration, blending_perc, relative_to_tcp=False, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Move_PTP', ['TPP' if relative_to_tcp else 'CPP', relative_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))

   def move_to_joint_angles_ptp(self, joint_angles_goal, speed_perc, acceleration_duration, blending_perc, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('PTP', ['JPP', joint_angles_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))

   def move_to_relative_joint_angles_ptp(self, relative_joint_angles_goal, speed_perc, acceleration_duration, blending_perc, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Move_PTP', ['JPP', relative_joint_angles_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))

   # ==== Path ====

   def move_to_point_path(self, tcp_point_goal, velocity, acceleration_duration, blending_perc):
      if blending_perc > 1.0: raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('PLine', ['CAP', tcp_point_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)]))

   def move_to_relative_point_path(self, relative_point_goal, velocity, acceleration_duration, blending_perc, relative_to_tcp=False):
      if blending_perc > 1.0: raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Move_PLine', ['TAP' if relative_to_tcp else 'CAP', relative_point_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)]))

   def move_to_joint_angles_path(self, joint_angles_goal, velocity, acceleration_duration, blending_perc):
      if blending_perc > 1.0: raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('PLine', ['JAP', joint_angles_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)]))

   def move_to_relative_joint_angles_path(self, relative_joint_angles_goal, velocity, acceleration_duration, blending_perc, use_precise_positioning=False):
      if blending_perc > 1.0: raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Move_PLine', ['JAP', relative_joint_angles_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))

   # ==== Line ====

   # NOTE: Speed could also be defined as a velocity
   # NOTE: Blending value could also be defined as a radius
   def move_to_point_line(self, tcp_point_goal, speed_perc, acceleration_duration, blending_perc, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Line', ['CPP', tcp_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))
      
   # NOTE: Speed could also be defined as a velocity
   # NOTE: Blending value could also be defined as a radius
   def move_to_relative_point_line(self, relative_point_goal, speed_perc, acceleration_duration, blending_perc, relative_to_tcp=False, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Move_Line', ['TPP' if relative_to_tcp else 'CPP', relative_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]))

   # ==== other move commmands ====

   # NOTE: Speed could also be defined as a velocity
   def move_on_circle(self, tcp_point_1, tcp_point_2, speed_perc, acceleration_duration, blending_perc, arc_angle, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0:
         raise TMSCTException('Percentages should have value between 0.0 and 1.0')
      return self._execute_command(('Circle', ['CPP', tcp_point_1, tcp_point_2, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), arc_angle, not use_precise_positioning]))


if __name__ == "__main__":
   # clnt = TMSCT_client(robot_ip='localhost', id='client_demo')
   # try: status = clnt.get_queue_tag_status(3)
   # except TechmanException as e: print(type(e).__name__ + ': ' + str(e))
   # print(f'Status: {status}')
   pass
