#!/usr/bin/python
# -*- coding: utf-8 -*-

# you should use multiple instance of redis, here just for travis-ci tests
servers = [
    {'name': 'node1', 'host': '127.0.0.1', 'port': 6379, 'db': 0},
    {'name': 'node2', 'host': '127.0.0.1', 'port': 6379, 'db': 1},
    {'name': 'node3', 'host': '127.0.0.1', 'port': 6379, 'db': 2},
]

try:
    from .local_config import *
except ImportError:
    pass
