#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redis_shard.shard import RedisShardAPI
from config import servers
import time

client = RedisShardAPI(servers)
client.set('test', 1)
print client.get('test')
client.zadd('testset', 'first', 1)
client.zadd('testset', 'second', 2)
print client.zrange('testset', 0, -1)
print client.zrank('testset', 'second')
print client.zrank('testset2', 'second')

client.set('foo', 2)
client.set('a{foo}', 5)
client.set('b{foo}', 5)
client.set('c{foo}', 5)
client.set('{foo}d', 6)
client.set('{foo}e', 7)
client.set('e{foo}f', 8)
print client.get_server_name('foo')
print client.get_server_name('c{foo}')
print client.get_server_name('{foo}d')
print client.get_server_name('{foo}e')
print client.get_server_name('e{foo}f')
t0 = time.time()
print client.tag_keys('*{foo}*')
t1 = time.time()
print t1 - t0
print client.keys('*{foo}*')
t2 = time.time()
print t2 - t1

print client.tag_mget('a{foo}', 'b{foo}', '{foo}d')
print client.tag_mget(['a{foo}', 'b{foo}', '{foo}d'])
