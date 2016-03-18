#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import functools
import redis
from multiprocessing.dummy import Pool as ThreadPool

from redis.client import Lock
from redis.sentinel import Sentinel

from .commands import SHARD_METHODS
from ._compat import basestring, iteritems
from .hashring import HashRing
from .helpers import format_servers
from .pipeline import Pipeline
from .sentinel import SentinelRedis

_findhash = re.compile('.*\{(.*)\}.*', re.I)


def list_or_args(keys, args):
    # returns a single list combining keys and args
    try:
        iter(keys)
        # a string can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, basestring):
            keys = [keys]
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


class RedisShardAPI(object):

    def __init__(self, servers, hash_method='crc32', sentinel=None, strict_redis=False):
        self.nodes = []
        self.connections = {}
        self.pool = None
        servers = format_servers(servers)
        if sentinel:
            sentinel = Sentinel(sentinel['hosts'], socket_timeout=sentinel.get('socket_timeout', 1))
        for server_config in servers:
            name = server_config.pop('name')
            server_config["max_connections"] = int(server_config.get("max_connections", 100))
            if name in self.connections:
                raise ValueError("server's name config must be unique")
            if sentinel:
                self.connections[name] = SentinelRedis(sentinel, name)
            elif strict_redis:
                self.connections[name] = redis.StrictRedis(**server_config)
            else:
                self.connections[name] = redis.Redis(**server_config)
            server_config['name'] = name
            self.nodes.append(name)
        self.ring = HashRing(self.nodes, hash_method=hash_method)

    def get_server_name(self, key):
        g = _findhash.match(key)
        if g is not None and len(g.groups()) > 0:
            key = g.groups()[0]
        name = self.ring.get_node(key)
        return name

    def get_server(self, key):
        name = self.get_server_name(key)
        return self.connections[name]

    def _build_pool(self):
        if self.pool is None:
            self.pool = ThreadPool(len(self.nodes))

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        server = self.get_server(key)
        f = getattr(server, method)
        return f(*args, **kwargs)

    def __wrap_eval(self, method, script_or_sha, numkeys, *keys_and_args):
        if numkeys != 1:
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        key = keys_and_args[0]
        server = self.get_server(key)
        f = getattr(server, method)
        return f(script_or_sha, numkeys, *keys_and_args)

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
        if method in SHARD_METHODS:
            return functools.partial(self.__wrap, method)
        elif method in ('eval', 'evalsha'):
            return functools.partial(self.__wrap_eval, method)
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

    def mget(self, keys, *args):
        """
        Returns a list of values ordered identically to ``keys``
        """
        args = list_or_args(keys, args)
        server_keys = {}
        ret_dict = {}
        for key in args:
            server_name = self.get_server_name(key)
            server_keys[server_name] = server_keys.get(server_name, [])
            server_keys[server_name].append(key)
        for server_name, sub_keys in iteritems(server_keys):
            values = self.connections[server_name].mget(sub_keys)
            ret_dict.update(dict(zip(sub_keys, values)))
        result = []
        for key in args:
            result.append(ret_dict.get(key, None))
        return result

    def mset(self, mapping):
        """
        Sets each key in the ``mapping`` dict to its corresponding value
        """
        servers = {}
        for key, value in mapping.items():
            server_name = self.get_server_name(key)
            servers.setdefault(server_name, [])
            servers[server_name].append((key, value))
        for name, items in servers.items():
            self.connections[name].mset(dict(items))
        return True

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

    def script_load(self, script):
        shas = []
        for node in self.nodes:
            server = self.connections[node]
            shas.append(server.script_load(script))
        if not all(x == shas[0] for x in shas):
            raise ValueError('not all server returned same sha')
        return shas[0]

    def haskey(self, key):
        server_name = self.get_server_name(key)
        return key in self.connections[server_name]

    def __delitem__(self, key):
        server_name = self.get_server_name(key)
        del self.connections[server_name][key]
