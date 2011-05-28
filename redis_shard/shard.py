#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import redis
from hashring import HashRing
import functools

_findhash = re.compile('.+\{(.*)\}.*', re.I)

class RedisShardAPI(object):

    def __init__(self,servers):
        self.pool = redis.ConnectionPool()
        nodes = []
        self.connections = {}
        for server in servers:
            conn = redis.Redis(host=server['host'], port=server['port'], db=server['db'],connection_pool=self.pool)
            name = server['name']
            if name in self.connections:
                raise ValueError("server's name config must be unique")
            self.connections[name] = conn
            nodes.append(name)
        self.ring = HashRing(nodes)

    def get_server(self, key):
        name = self.ring.get_node(key)
        return self.connections[name]

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        g = _findhash.match(key)
        if g != None and len(g.groups()) > 0:
            key = g.groups()[0]
        server = self.get_server(key)
        f = getattr(server, method)
        return f(*args, **kwargs)

    def __getattr__(self, method):
        if method in [
            "get", "set", "getset",
            "setnx", "setex",
            "incr", "decr", "exists",
            "delete", "get_type", "rename",
            "expire", "ttl", "push",
            "llen", "lrange", "ltrim",
            "lindex", "pop", "lset",
            "lrem", "sadd", "srem",
            "sismember", "smembers",
            "zadd", "zrem", "zincr",
            "zrange", "zrevrange", "zrangebyscore",
            "zremrangebyscore", "zcard", "zscore",
            "hget", "hset", "hdel", "hincrby", "hlen",
            "hkeys", "hvals", "hgetall", "hexists", "hmget", "hmset",
            "publish",
            ]:
            return functools.partial(self.__wrap, method)
        else:
            raise NotImplementedError("method '%s' cannot be sharded" % method)

