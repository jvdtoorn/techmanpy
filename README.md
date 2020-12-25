# Python Driver for Techman Robots

This repository contains a communication driver for Techman robots written in Python.  
It is inspired by the official [tmr_ros1](https://github.com/TechmanRobotInc/tmr_ros1) C++ communication driver and provides easy-to-use communication serialisation and deserialisation.

## Requirements
**TMFlow:** `1.80` or higher  
**Python:** `3.7` or higher

## Installation
```
$ python3 -m pip install techmanpy
```

## Test connection with TMFlow
To verify that your connection with the robot is all set-up:
```
$ python3 test_connection.py <robot IP address>
```