#!/usr/bin/env python

import sys
import asyncio

from .stateful_client import *
from ..packets import *
from ..exceptions import *

class TMSCT_commands:

   # ==== general commmands ====

   def exit_listen(self):
      return ('ScriptExit', [])

   def set_queue_tag(self, tag_id, wait_for_completion=False):
      return ('QueueTag', [tag_id, 1 if wait_for_completion else 0])

   def wait_for_queue_tag(self, tag_id, timeout=-1):
      return ('WaitQueueTag', [tag_id, int(timeout)])

   def stop_motion(self):
      return ('StopAndClearBuffer', [])

   def pause_project(self):
      return ('Pause', [])

   def resume_project(self):
      return ('Resume', [])

   def set_base(self, base):
      if isinstance(base, list) and len(base) != 6:
         raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('ChangeBase', [base])

   def set_tcp(self, tcp, weight=None, inertia=None):
      if isinstance(tcp, list) and len(tcp) != 6:
         raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      arglist = [tcp]
      if weight is not None: arglist.append(weight)
      if inertia is not None: arglist.append(inertia)
      return ('ChangeTCP', arglist)

   def set_load_weight(self, weight):
      return ('ChangeLoad', [weight])

   # ==== PVT ====

   def enter_point_pvt_mode(self):
      return ('PVTEnter', [1])

   def add_pvt_point(self, tcp_point_goal, tcp_point_velocities_goal, duration):
      if len(tcp_point_goal) != 6 or len(tcp_point_velocities_goal) != 6:
         raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('PVTPoint', [tcp_point_goal, tcp_point_velocities_goal, duration/1000.0])

   def enter_joint_pvt_mode(self):
      return ('PVTEnter', [0])

   def add_pvt_joint_angles(self, joint_angles_goal, joint_angle_velocities_goal, duration):
      if len(joint_angles_goal) != 6 or len(joint_angle_velocities_goal) != 6:
         raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('PVTPoint', [joint_angles_goal, joint_angle_velocities_goal, duration/1000.0])

   def exit_pvt_mode(self):
      return ('PVTExit', [])

   def pause_pvt_mode(self):
      return ('PVTPause', [])

   def resume_pvt_mode(self):
      return ('PVTResume', [])

   # ==== PTP ====

   def move_to_point_ptp(self, tcp_point_goal, speed_perc, acceleration_duration, blending_perc=0.0, use_precise_positioning=False, pose_goal=None):
      if speed_perc > 1.0 or blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(tcp_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      arglist = ['CPP', tcp_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning]
      if pose_goal is not None: arglist.append(pose_goal)
      return ('PTP', arglist)

   def move_to_relative_point_ptp(self, relative_point_goal, speed_perc, acceleration_duration, blending_perc=0.0, relative_to_tcp=False, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(relative_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('Move_PTP', ['TPP' if relative_to_tcp else 'CPP', relative_point_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning])

   def move_to_joint_angles_ptp(self, joint_angles_goal, speed_perc, acceleration_duration, blending_perc=0.0, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(joint_angles_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('PTP', ['JPP', joint_angles_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning])

   def move_to_relative_joint_angles_ptp(self, relative_joint_angles_goal, speed_perc, acceleration_duration, blending_perc=0.0, use_precise_positioning=False):
      if speed_perc > 1.0 or blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(relative_joint_angles_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('Move_PTP', ['JPP', relative_joint_angles_goal, int(100 * speed_perc), int(acceleration_duration), int(100 * blending_perc), not use_precise_positioning])

   # ==== Path ====

   def move_to_point_path(self, tcp_point_goal, velocity, acceleration_duration, blending_perc=0.0):
      if blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(tcp_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('PLine', ['CAP', tcp_point_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)])

   def move_to_relative_point_path(self, relative_point_goal, velocity, acceleration_duration, blending_perc=0.0, relative_to_tcp=False):
      if blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(relative_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('Move_PLine', ['TAP' if relative_to_tcp else 'CAP', relative_point_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)])

   def move_to_joint_angles_path(self, joint_angles_goal, velocity, acceleration_duration, blending_perc=0.0):
      if blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(joint_angles_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('PLine', ['JAP', joint_angles_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)])

   def move_to_relative_joint_angles_path(self, relative_joint_angles_goal, velocity, acceleration_duration, blending_perc=0.0):
      if blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(relative_joint_angles_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      return ('Move_PLine', ['JAP', relative_joint_angles_goal, int(velocity), int(acceleration_duration), int(100 * blending_perc)])

   # ==== Line ====

   def move_to_point_line(self, tcp_point_goal, speed, acceleration_duration, blending=0.0, speed_is_velocity=False, blending_is_radius=False, use_precise_positioning=False):
      if (not speed_is_velocity and speed > 1.0) or (not blending_is_radius and blending > 1.0): raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(tcp_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      data_mode = f'C{"A" if speed_is_velocity else "P"}{"R" if blending_is_radius else "P"}'
      speed = int(speed if speed_is_velocity else (100 * speed))
      blending = int(blending if blending_is_radius else (100 * blending))
      return ('Line', [data_mode, tcp_point_goal, speed, int(acceleration_duration), blending, not use_precise_positioning])

   def move_to_relative_point_line(self, relative_point_goal, speed, acceleration_duration, blending=0.0, relative_to_tcp=False, speed_is_velocity=False, blending_is_radius=False, use_precise_positioning=False):
      if (not speed_is_velocity and speed > 1.0) or (not blending_is_radius and blending > 1.0): raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(relative_point_goal) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      data_mode = f'{"T" if relative_to_tcp else "C"}{"A" if speed_is_velocity else "P"}{"R" if blending_is_radius else "P"}'
      speed = int(speed if speed_is_velocity else (100 * speed))
      blending = int(blending if blending_is_radius else (100 * blending))
      return ('Move_Line', [data_mode, relative_point_goal, speed, int(acceleration_duration), blending, not use_precise_positioning])

   # ==== Circle ====

   def move_on_circle(self, tcp_point_1, tcp_point_2, speed, acceleration_duration, arc_angle=0, blending_perc=0.0, speed_is_velocity=False, use_precise_positioning=False):
      if (not speed_is_velocity and speed > 1.0) or blending_perc > 1.0: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): percentages should have value between 0.0 and 1.0')
      if len(tcp_point_1) != 6 or len(tcp_point_2) != 6: raise TMSCTError(f'{sys._getframe().f_code.co_name}(): position array should have exactly 6 elements')
      speed = int(speed if speed_is_velocity else (100 * speed))
      return ('Circle', ['CAP' if speed_is_velocity else 'CPP', tcp_point_1, tcp_point_2, speed, int(acceleration_duration), int(100 * blending_perc), arc_angle, not use_precise_positioning])

class TMSCT_client(StatefulClient):

   PORT=5890

   def __init__(self, *, robot_ip, client_id='SCTpy', conn_timeout=3, suppress_warns=False):
      super().__init__(robot_ip=robot_ip, robot_port=self.PORT, client_id=client_id, conn_timeout=conn_timeout)
      self._client_id = client_id
      self._suppress_warns = suppress_warns

   def _on_connection(self, reader, writer):
      return TMSCT_connection(self._client_id, reader, writer, self._conn_timeout, self._suppress_warns)

class TMSCT_connection(StatefulConnection, TMSCT_commands):

   def __init__(self, client_id, reader, writer, conn_timeout, suppress_warns):
      super().__init__(client_id, reader, writer, conn_timeout)
      self._suppress_warns = suppress_warns

   def start_transaction(self): return TMSCT_transaction(self)

   async def _execute(self, commands):
      if not isinstance(commands, list): commands = [commands]
      commands = list(map(self._unfold_command, commands))
      # Build TMSCT packet
      handle_id = self._obtain_handle_id()
      req = TMSCT_packet(handle_id, TMSCT_type.REQUEST, commands)
      # Submit
      res = TMSCT_packet(await self.send(req))
      # Parse response
      assert res.handle_id == handle_id
      assert res.ptype == TMSCT_type.RESPONSE
      if len(res.lines) > 0:
         commands = [req.commands[i-1] for i in res.lines]
         enc_cmnds = list(map(req._encode_command, commands))
         if res.status == TMSCT_status.SUCCESS:
            if not self._suppress_warns:
               if len(res.lines) == 1:
                  print(f'[TMSCT_client] WARN: The command \'{enc_cmnds[0]}\' resulted in a warning')
               elif len(res.lines) > 1: print(f'[TMSCT_client] WARN: The following commands resulted in a warning: {enc_cmnds}')
         if res.status == TMSCT_status.ERROR:
            if len(res.lines) == 1: raise TMSCTError(f'The command \'{enc_cmnds[0]}\' resulted in an error')
            else: raise TMSCTError(f'The following commands resulted in an error: {enc_cmnds}')

   def _flatten(self, seq, scalarp=None):
      for item in seq:
         if item is None or isinstance(item, str) or not hasattr(item, '__iter__'): yield item
         else: yield from self._flatten(item)

   def _unfold_command(self, command):
      return (command[0], list(self._flatten(command[1])))

   def __getattribute__(self, attr):
      if hasattr(TMSCT_commands, attr):
         def caller(*args, **kwargs): return self._meta_execute(getattr(TMSCT_commands, attr), *args, **kwargs)
         return caller
      else: return super().__getattribute__(attr)

   async def _meta_execute(self, command_func, *args, **kwargs):
      return await self._execute(command_func(self, *args, **kwargs))

class TMSCT_transaction(TMSCT_commands):

   def __init__(self, conn):
      self._conn = conn
      self._transaction = []
      self._did_submit = False

   async def submit(self):
      if self._did_submit: raise TMSCTError('Transaction was already submitted')
      self._did_submit = True
      return await self._conn._execute(self._transaction)

   def __getattribute__(self, attr):
      if hasattr(TMSCT_commands, attr):
         def caller(*args, **kwargs): return self._meta_execute(getattr(TMSCT_commands, attr), *args, **kwargs)
         return caller
      else: return super().__getattribute__(attr)

   def _meta_execute(self, command_func, *args, **kwargs):
      if self._did_submit: raise TMSCTError('Transaction was already submitted')
      self._transaction.append(command_func(self, *args, **kwargs))
