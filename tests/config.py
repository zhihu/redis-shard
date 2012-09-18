#!/usr/bin/python
# -*- coding: utf-8 -*-

servers = [
    {'name':'node1', 'host':'127.0.0.1', 'port':6379, 'db':0},
    {'name':'node2', 'host':'127.0.0.1', 'port':6380, 'db':0},
    {'name':'node3', 'host':'127.0.0.1', 'port':6381, 'db':0},
]

try:
    from .local_config import *
except ImportError:
    pass
