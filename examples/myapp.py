#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redis_shard.shard import RedisShardAPI
from config import servers

client = RedisShardAPI(servers)
client.set('test',1)
print client.get('test')
client.zadd('testset','first',1)
client.zadd('testset','second',2)
print client.zrange('testset',0,-1)

client.set('foo',2)
client.set('a{foo}',5)
client.set('b{foo}',5)
client.set('c{foo}',5)
print client.get('foo')
