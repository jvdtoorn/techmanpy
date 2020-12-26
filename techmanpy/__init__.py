#!/usr/bin/env python

from .exceptions import *
from .packets import *
from .clients import *

def connect_sta(*, robot_ip, conn_timeout=3):
    return TMSTA_client(robot_ip=robot_ip, conn_timeout=conn_timeout)

def connect_svr(*, robot_ip, client_id='SVRpy', conn_timeout=3):
    return TMSVR_client(robot_ip=robot_ip, client_id=client_id, conn_timeout=conn_timeout)

def connect_sct(*, robot_ip, client_id='SCTpy', conn_timeout=3, suppress_warns=False):
    return TMSCT_client(robot_ip=robot_ip, client_id=client_id, conn_timeout=conn_timeout, suppress_warns=suppress_warns)
