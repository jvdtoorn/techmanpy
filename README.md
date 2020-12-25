# Python Driver for Techman Robots

This repository contains a communication driver for Techman robots written in Python.  
It is inspired by the official [tmr_ros1](https://github.com/TechmanRobotInc/tmr_ros1) C++ communication driver and provides easy-to-use communication serialisation and deserialisation.

## Test connection
Before using this driver, make sure you are connected to your Techman robot.  
This can be verified by running:   
```
$ python scripts/test_connection.py <robot IP address>
```