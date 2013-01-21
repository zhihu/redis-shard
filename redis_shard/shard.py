#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import redis
from redis.client import Lock
from hashring import HashRing
import functools
from pipeline import Pipeline

from .helpers import format_config

_findhash = re.compile('.*\{(.*)\}.*', re.I)


class RedisShardAPI(object):

    SHARD_METHODS = set([
        "get", "set", "getset", "append", "getrange",
        "setnx", "setex",
        "incr", "decr", "exists",
        "delete", "get_type", "type", "rename",
        "expire", "ttl", "push", "persist",
        "llen", "lrange", "ltrim", "lpush", "lpop",
        "lindex", "pop", "lset",
        "lrem", "sadd", "srem", "scard",
        "sismember", "smembers",
        "zadd", "zrem", "zincrby", "zincr", "zrank",
        "zrange", "zrevrange", "zrangebyscore", "zremrangebyrank", "zrevrangebyscore",
        "zremrangebyscore", "zcard", "zscore", "zcount",
        "hget", "hset", "hdel", "hincrby", "hlen",
        "hkeys", "hvals", "hgetall", "hexists", "hmget", "hmset",
        "publish", "rpush", "rpop"
    ])

    def __init__(self, settings=None):
        self.nodes = []
        self.connections = {}
        settings = format_config(settings)
        for server in settings:
            name = server.get('name')
            conn = redis.Redis(host=server.get('host'),
                               port=server.get('port'),
                               db=server.get('db'),
                               password=server.get('password'),
                               socket_timeout=server.get('socket_timeout'),
                               unix_socket_path=server.get('unix_socket_path'),
                               )
            server['name'] = name
            if name in self.connections:
                raise ValueError("server's name config must be unique")
            self.connections[name] = conn
            self.nodes.append(name)
        self.ring = HashRing(self.nodes)

    def get_server_name(self, key):
        g = _findhash.match(key)
        if g is not None and len(g.groups()) > 0:
            key = g.groups()[0]
        name = self.ring.get_node(key)
        return name

    def get_server(self, key):
        name = self.get_server_name(key)
        return self.connections[name]

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        server = self.get_server(key)
        f = getattr(server, method)
        return f(*args, **kwargs)

    def __wrap_tag(self, method, *args, **kwargs):
        key = args[0]
        if isinstance(key, basestring) and '{' in key:
            server = self.get_server(key)
        elif isinstance(key, list) and '{' in key[0]:
            server = self.get_server(key[0])
        else:
            raise ValueError("method '%s' requires tag key params as its arguments" % method)
        method = method.lstrip("tag_")
        f = getattr(server, method)
        return f(*args, **kwargs)

    def __getattr__(self, method):
        if method in self.SHARD_METHODS:
            return functools.partial(self.__wrap, method)
        elif method.startswith("tag_"):
            return functools.partial(self.__wrap_tag, method)
        else:
            raise NotImplementedError("method '%s' cannot be sharded" % method)

    #########################################
    ###  some methods implement as needed ###
    ########################################
    def brpop(self, key, timeout=0):
        if not isinstance(key, basestring):
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        server = self.get_server(key)
        return server.brpop(key, timeout)

    def blpop(self, key, timeout=0):
        if not isinstance(key, basestring):
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        server = self.get_server(key)
        return server.blpop(key, timeout)

    def keys(self, key):
        _keys = []
        for node in self.nodes:
            server = self.connections[node]
            _keys.extend(server.keys(key))
        return _keys

    def flushdb(self):
        for node in self.nodes:
            server = self.connections[node]
            server.flushdb()

    def lock(self, name, timeout=None, sleep=0.1):
        """
        Return a new Lock object using key ``name`` that mimics
        the behavior of threading.Lock.

        If specified, ``timeout`` indicates a maximum life for the lock.
        By default, it will remain locked until release() is called.

        ``sleep`` indicates the amount of time to sleep per loop iteration
        when the lock is in blocking mode and another client is currently
        holding the lock.
        """
        return Lock(self, name, timeout=timeout, sleep=sleep)

    def pipeline(self):
        return Pipeline(self)
