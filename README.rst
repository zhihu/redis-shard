Redis Shard 
==============
A redis sharding api. Sharding is done based on the CRC32 checksum of a key or key tag ("key{key_tag}"),
according to this article http://antirez.com/post/redis-presharding.html .

Useage
==============
Please see the `examples` directory for detail.

>>> from redis_shard.shard import RedisShardAPI
>>> clients = [
    ...    {'host':'127.0.0.1','port':10000,'db':0},
    ...    {'host':'127.0.0.1','port':11000,'db':0},
    ...    {'host':'127.0.0.1','port':12000,'db':0},
    ...    {'host':'127.0.0.1','port':13000,'db':0},
    ...    ]
>>> 
>>> client = RedisShardAPI(clients)
>>> client.set('test',1)
>>> print client.get('test')
>>> client.zadd('testset','first',1)
>>> client.zadd('testset','second',2)
>>> print client.zrange('testset',0,-1)

Hash tags
----------------
see article `http://antirez.com/post/redis-presharding.html` for detail.

>>> client.set('foo',2)
>>> client.set('a{foo}',5)
>>> client.set('b{foo}',5)
>>> client.set('c{foo}',5)
