<p align="left">
  <img src='https://raw.githubusercontent.com/jvdtoorn/techmanpy/master/img/logo.png'>
</p>

[![Python version](https://img.shields.io/badge/python-3.8%2B-blue)](https://pypi.org/project/techmanpy)
[![pypi version](https://img.shields.io/badge/pypi-v1.0-blue)](https://pypi.org/project/techmanpy)
[![License](https://img.shields.io/badge/license-MIT-red)](https://github.com/jvdtoorn/techmanpy/blob/master/LICENSE)

## What is `techmanpy`?

`techmanpy` is an easy-to-use communication driver for Techman robots written in Python.

With it, the state of the robot can be monitored, internal parameters can be changed and move commands can be executed. With these features it acts as a solid foundation for any custom higher-level script.

By using `asyncio` for all socket communications, it provides an elegant coroutine-based API.

Read the full documentation at the [Wiki](https://github.com/jvdtoorn/techmanpy/wiki).

Here's how to command your robot to move:
```Python
#!/usr/bin/env python

import asyncio
import techmanpy

async def move():
   async with techmanpy.connect_sct(robot_ip='<robot IP address>') as conn:
      await conn.move_to_joint_angles_ptp([10, -10, 10, -10, 10, -10], 0.10, 200, 0)

asyncio.run(move())
```

And here's how to listen to the TMFlow server:
```Python
#!/usr/bin/env python

import asyncio
import techmanpy

async def listen():
   async with techmanpy.connect_svr(robot_ip='<robot IP address>') as conn:
      conn.add_broadcast_callback(print)
      await conn.keep_alive()

asyncio.run(listen())
```

## Requirements
**TMFlow:** `1.80+`  
**Python:** &nbsp;`3.8+`

## Installation
```
$ python3 -m pip install techmanpy
```

## Test connection with TMFlow
To verify that your connection with the robot is all set-up:
```
$ python3 test_connection.py <robot IP address>
```

## What else?
Bug reports, patches and suggestions are welcome! Feel free to open an [issue](https://github.com/jvdtoorn/techmanpy/issues/new) or send a [pull request](https://github.com/jvdtoorn/techmanpy/pulls).

`techmanpy` is not affiliated, authorized, or in any way officially connected with [Techman Robot](https://www.tm-robot.com/en/). Use this software at your own risk, it did not undergo any official quality assurance.

This package is released under the [MIT license](https://github.com/jvdtoorn/techmanpy/blob/master/LICENSE).
