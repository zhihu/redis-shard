#!/usr/bin/env python
# encoding: utf-8
from redis import Redis
from .commands import READ_COMMANDS


class SentinelRedis(object):

    def __init__(self, sentinel, service_name):
        self.master = sentinel.master_for(service_name, redis_class=Redis)
        self.slave = sentinel.slave_for(service_name, redis_class=Redis)

    def __getattr__(self, method):
        if method in READ_COMMANDS:
            return getattr(self.slave, method)
        else:
            return getattr(self.master, method)
