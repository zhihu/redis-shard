#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import redis
from hashring import HashRing
import functools

_findhash = re.compile('.+\{(.*)\}.*', re.I)

class RedisShardAPI(object):

    def __init__(self,clients):
        self.pool = redis.ConnectionPool()
        nodes = []
        for client in clients:
            conn = redis.Redis(host=client['host'], port=client['port'], db=client['db'],connection_pool=self.pool)
            nodes.append(conn)
        self.ring = HashRing(nodes)

    def get_node(self, key):
        return self.ring.get_node(key)

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        g = _findhash.match(key)
        if g != None and len(g.groups()) > 0:
            key = g.groups()[0]
        node = self.get_node(key)
        f = getattr(node, method)
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

