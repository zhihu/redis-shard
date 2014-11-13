Redis Shard 
==============

A Redis sharding implementation.

.. image:: https://travis-ci.org/zhihu/redis-shard.png?branch=master
   :alt: Build Status

Usage
==============

First, Create an RedisShardAPI instance with multiple nodes, node ``name`` **must be unique**::

    from redis_shard.shard import RedisShardAPI
    
    servers = [
        {'name':'server1', 'host':'127.0.0.1', 'port':10000, 'db':0},
        {'name':'server2', 'host':'127.0.0.1', 'port':11000, 'db':0},
        {'name':'server3', 'host':'127.0.0.1', 'port':12000, 'db':0},
    ]
    
    client = RedisShardAPI(servers)

Then, you can manipulate the Redis cluster as you use `redis-py <https://github.com/andymccurdy/redis-py>`_::

    client.set('test', 1)
    client.get('test')  # 1
    client.zadd('testset', 'first', 1)
    client.zadd('testset', 'second', 2)
    client.zrange('testset', 0, -1)  # [first, second]


Hash Tags
----------------

If you want to store specific keys on one node for some reason, you should use Hash Tags::

    client.set('foo', 2)
    client.set('a{foo}', 5)
    client.set('b{foo}', 5)
    client.set('{foo}d', 5)
    client.set('d{foo}e', 5)

    client.get_server_name('foo') == client.get_server_name('a{foo}') == client.get_server_name('{foo}d') \
            == client.get_server_name('d{foo}e')  # True


Config Format
-------------------

`RedisShardAPI` supports 3 kinds of config format:

- list::

    servers = [
        {'name':'node1','host':'127.0.0.1','port':10000,'db':0},
        {'name':'node2','host':'127.0.0.1','port':11000,'db':0},
        {'name':'node3','host':'127.0.0.1','port':12000,'db':0},
    ]

- dict::

    servers = {
        'node1': {'host':'127.0.0.1','port':10000,'db':0},
        'node2': {'host':'127.0.0.1','port':11000,'db':0},
        'node3': {'host':'127.0.0.1','port':12000,'db':0},
    }

- url_schema::

    servers = [
        'redis://127.0.0.1:10000/0?name=node1',
        'redis://127.0.0.1:11000/0?name=node2',
        'redis://127.0.0.1:12000/0?name=node3'
    ]
