#!/usr/bin/env python
SHARD_METHODS = frozenset(['restore',
                           'debug object',
                           'hincrby',
                           'zrevrank',
                           'zcount',
                           'move',
                           'pop',
                           'hexists',
                           'get_type',
                           'incrbyfloat',
                           'ttl',
                           'sinter',
                           'getbit',
                           'decr',
                           'rpush',
                           'pttl',
                           'zscore',
                           'delete',
                           'dump',
                           'zincrby',
                           'zrevrangebyscore',
                           'persist',
                           'zrem',
                           'zadd',
                           'linsert',
                           'sort',
                           'zcard',
                           'bitcount',
                           'get',
                           'setnx',
                           'watch',
                           'incrby',
                           'lindex',
                           'hget',
                           'hlen',
                           'expireat',
                           'type',
                           'zincr',
                           'lset',
                           'hkeys',
                           'setrange',
                           'del',
                           'hset',
                           'decrby',
                           'zrange',
                           'set',
                           'exists',
                           'hincrbyfloat',
                           'pexpireat',
                           'hvals',
                           'setex',
                           'sdiff',
                           'blpop',
                           'strlen',
                           'append',
                           'srem',
                           'pexpire',
                           'getrange',
                           'zrevrange',
                           'zremrangebyscore',
                           'hsetnx',
                           'lpushx',
                           'rpushx',
                           'hmset',
                           'srandmember',
                           'sismember',
                           'getset',
                           'smembers',
                           'zrank',
                           'psetex',
                           'zremrangebyrank',
                           'sadd',
                           'ltrim',
                           'spop',
                           'incr',
                           'expire',
                           'brpop',
                           'lrange',
                           'sunion',
                           'setbit',
                           'zrangebyscore',
                           'rpop',
                           'lrem',
                           'lpop',
                           'hgetall',
                           'lpush',
                           'hmget',
                           'push',
                           'hdel',
                           'scard',
                           'llen',
                           'publish'])


READ_COMMANDS = frozenset([
    'info', 'smembers', 'hlen', 'hmget', 'srandmember', 'hvals', 'randomkey', 'strlen',
    'dbsize', 'keys', 'ttl', 'lindex', 'type', 'llen', 'dump', 'scard', 'echo', 'lrange',
    'zcount', 'exists', 'sdiff', 'zrange', 'mget', 'zrank', 'get', 'getbit', 'getrange',
    'zrevrange', 'zrevrangebyscore', 'hexists', 'object', 'sinter', 'zrevrank', 'hget',
    'zscore', 'hgetall', 'sismember'])
