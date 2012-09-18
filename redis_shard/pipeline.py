
import functools


class Pipeline(object):
    def __init__(self, shard_api):
        self.shard_api = shard_api
        self.pipelines = {}

    def get_pipeline(self, key):
        name = self.shard_api.get_server_name(key)
        if name not in self.pipelines:
            self.pipelines[name] = self.shard_api.connections[name].pipeline()
        return self.pipelines[name]

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        pipeline = self.get_pipeline(key)
        f = getattr(pipeline, method)
        return f(*args, **kwargs)

    def __wrap_tag(self, method, *args, **kwargs):
        key = args[0]
        if isinstance(key, basestring) and '{' in key:
            pipeline = self.get_pipeline(key)
        elif isinstance(key, list) and '{' in key[0]:
            pipeline = self.get_pipeline(key[0])
        else:
            raise ValueError("method '%s' requires tag key params as its arguments" % method)
        method = method.lstrip("tag_")
        f = getattr(pipeline, method)
        return f(*args, **kwargs)

    def __hop_in(self, method, *args, **kwargs):
        if not isinstance(args[1], str):
            key = str(args[1])
        else:
            key = args[1]
        try:
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the second argument" % method)
        pipeline = self.get_pipeline(key)
        if method == "hget_in":
            method = "hget"
        elif method == "hset_in":
            method = "hset"
        elif method == "hdel_in":
            method = "hdel"
        else:
            print "you can't be here"
        f = getattr(pipeline, method)
        return f(*args, **kwargs)

    def __qop_in(self, method, *args, **kwargs):
        key = "queue"
        pipeline = self.get_pipeline(key)
        if method == "rpush_in":
            method = "rpush"
        elif method == "blpop_in":
            method = "blpop"
        else:
            print "you can't be here"
        f = getattr(pipeline, method)
        return f(*args, **kwargs)

    def execute(self):
        results = []
        for name, pipeline in self.pipelines.iteritems():
            result = pipeline.execute()
            results.extend(list(result))
        return results

    def __getattr__(self, method):
        if method in [
            "get", "set", "getset",
            "setnx", "setex",
            "incr", "decr", "exists",
            "delete", "get_type", "type", "rename",
            "expire", "ttl", "push", "persist",
            "llen", "lrange", "ltrim", "lpush", "lpop",
            "lindex", "pop", "lset",
            "lrem", "sadd", "srem", "scard",
            "sismember", "smembers",
            "zadd", "zrem", "zincr", "zincrby", "zrank",
            "zrange", "zrevrange", "zrangebyscore", "zremrangebyrank", "zrevrangebyscore",
            "zremrangebyscore", "zcard", "zscore", "zcount",
            "hget", "hset", "hdel", "hincrby", "hlen",
            "hkeys", "hvals", "hgetall", "hexists", "hmget", "hmset",
            "publish", "rpush", "rpop"
        ]:
            return functools.partial(self.__wrap, method)
        elif method.startswith("tag_"):
            return functools.partial(self.__wrap_tag, method)
        elif method in ["hget_in", "hset_in", "hdel_in"]:
            return functools.partial(self.__hop_in, method)
        elif method in ["blpop_in", "rpush_in"]:
            return functools.partial(self.__qop_in, method)
        else:
            raise NotImplementedError(
                "method '%s' cannot be pipelined" % method)
