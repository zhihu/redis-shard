#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import redis
from hashring import HashRing
import functools

_findhash = re.compile('.*\{(.*)\}.*', re.I)

class RedisShardAPI(object):

    def __init__(self,servers):
        VERSION = tuple(map(int, redis.__version__.split('.')))
        self.nodes = []
        self.connections = {}
        if VERSION < (2,4,0):
            self.pool = redis.ConnectionPool()
        else:
            self.pool = None
        if isinstance(servers,list):
            for server in servers:
                conn = redis.Redis(host=server['host'], port=server['port'], db=server['db'],connection_pool=self.pool,
                                   password=server.get('password'), socket_timeout=server.get('socket_timeout'))
                name = server['name']
                if name in self.connections:
                    raise ValueError("server's name config must be unique")
                self.connections[name] = conn
                self.nodes.append(name)
        elif isinstance(servers,dict):
            for server_name,server in servers.items():
                conn = redis.Redis(host=server['host'], port=server['port'], db=server['db'],connection_pool=self.pool,
                                   password=server.get('password'), socket_timeout=server.get('socket_timeout'))
                name = server_name
                if name in self.connections:
                    raise ValueError("server's name config must be unique")
                self.connections[name] = conn
                self.nodes.append(name)
        else:
            raise ValueError("server's config must be list or dict")
        self.ring = HashRing(self.nodes)

    def get_server_name(self, key):
        g = _findhash.match(key)
        if g != None and len(g.groups()) > 0:
            key = g.groups()[0]
        name = self.ring.get_node(key)
        return name

    def get_server(self,key):
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

    def __wrap_tag(self,method,*args,**kwargs):
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

    def __hop_in(self, method, *args, **kwargs):
        '''
        使用field作为查询hashring的key
        '''
        if not isinstance(args[1], str):
            key = str(args[1])
        else:
            key = args[1]
        try:
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the second argument" % method)
        server = self.get_server(key)
        if method == "hget_in":
            method = "hget"
        elif method == "hset_in":
            method = "hset"
        elif method == "hdel_in":
            method = "hdel"
        else:
            print "you can't be here"
        f = getattr(server, method)
        return f(*args, **kwargs)
        
    def __qop_in(self, method, *args, **kwargs):
        '''
        指定key值所对应的hashring上的一个节点作为队列服务器
        '''    
        key = "queue"
        server = self.get_server(key)
        if method == "rpush_in":
            method = "rpush"
        elif method == "blpop_in":
            method = "blpop"
        else:
            print "you can't be here"
        f = getattr(server, method)
        return f(*args, **kwargs)
        
    def __getattr__(self, method):
        if method in [
            "get", "set", "getset",
            "setnx", "setex",
            "incr", "decr", "exists",
            "delete", "get_type", "type", "rename",
            "expire", "ttl", "push","persist",
            "llen", "lrange", "ltrim","lpush","lpop",
            "lindex", "pop", "lset",
            "lrem", "sadd", "srem","scard",
            "sismember", "smembers",
            "zadd", "zrem", "zincr","zrank",
            "zrange", "zrevrange", "zrangebyscore","zremrangebyrank","zrevrangebyscore",
            "zremrangebyscore", "zcard", "zscore","zcount",
            "hget", "hset", "hdel", "hincrby", "hlen",
            "hkeys", "hvals", "hgetall", "hexists", "hmget", "hmset",
            "publish","rpush","rpop"
            ]:
            return functools.partial(self.__wrap, method)
        elif method.startswith("tag_"):
            return functools.partial(self.__wrap_tag, method)
        elif method in ["hget_in", "hset_in", "hdel_in"]:
            return functools.partial(self.__hop_in, method)
        elif method in ["blpop_in", "rpush_in"]:
            return functools.partial(self.__qop_in, method)
        else:
            raise NotImplementedError("method '%s' cannot be sharded" % method)


    #########################################
    ###  some methods implement as needed ###
    ########################################

    def brpop(self,key, timeout=0):
        if not isinstance(key, basestring):
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        server = self.get_server(key)
        return server.brpop(key,timeout)

    def blpop(self,key, timeout=0):
        if not isinstance(key, basestring):
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        server = self.get_server(key)
        return server.blpop(key,timeout)

    def keys(self,key):
        _keys = []
        for node in self.nodes:
            server = self.connections[node]
            _keys.extend(server.keys(key))
        return _keys

    def flushdb(self):
        for node in self.nodes:
            server = self.connections[node]
            server.flushdb()

    def hgetall_in(self, key):
        result = {}
        for node in self.nodes:
            server = self.connections[node]
            result.update(server.hgetall(key))
        return result

    def hmget_in(self, key, fields):
        result = {}
        node_field = {}
        for field in fields:
            node = self.get_server_name(field)
            node_field.setdefault(node, [])
            node_field[node].append(field)

        for node, field_list in node_field.items():
            server = self.connections[node]
            value = server.hmget(key, field_list)
            for i in range(len(field_list)):
                result[field_list[i]]=value[i]
        return result
