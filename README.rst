Redis Shard
###########

.. image:: https://img.shields.io/travis/zhihu/redis-shard.svg?style=flat
   :target: https://travis-ci.org/zhihu/redis-shard
   :alt: Build Status

.. image:: https://img.shields.io/pypi/v/redis-shard.svg?style=flat
    :target: https://pypi.python.org/pypi/redis-shard
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/redis-shard.svg?style=flat
    :target: https://pypi.python.org/pypi/redis-shard
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/redis-shard.svg?style=flat
    :target: https://pypi.python.org/pypi/redis-shard
    :alt: License

A Redis sharding implementation.

Redis is great. It's fast, lightweight and easy to use. But when we want to store
a mass of data into one single instance, we may encounter some problems such as performance
degradation and slow recovery and we need to scale it.

Usage
=====

First, Create an RedisShardAPI instance with multiple nodes, node ``name`` **must be unique**::

    from redis_shard.shard import RedisShardAPI

    servers = [
        {'name': 'server1', 'host': '127.0.0.1', 'port': 10000, 'db': 0},
        {'name': 'server2', 'host': '127.0.0.1', 'port': 11000, 'db': 0},
        {'name': 'server3', 'host': '127.0.0.1', 'port': 12000, 'db': 0},
    ]

    client = RedisShardAPI(servers, hash_method='md5')

Then, you can access the Redis cluster as you use `redis-py <https://github.com/andymccurdy/redis-py>`_::

    client.set('test', 1)
    client.get('test')  # 1
    client.zadd('testset', 'first', 1)
    client.zadd('testset', 'second', 2)
    client.zrange('testset', 0, -1)  # [first, second]


Hash Tags
---------

If you want to store specific keys on one node for some reason (such as you prefer single instance pipeline, or
you want to use multi-keys command such as ``sinter``), you should use Hash Tags::

    client.set('foo', 2)
    client.set('a{foo}', 5)
    client.set('b{foo}', 5)
    client.set('{foo}d', 5)
    client.set('d{foo}e', 5)

    client.get_server_name('foo') == client.get_server_name('a{foo}') == client.get_server_name('{foo}d') \
        == client.get_server_name('d{foo}e')  # True

The string in a braces of a key is the Hash Tag of the key. The hash of a Hash Tag will be treated the hash of the key.
So, keys ``foo``, ``bar{foo}`` and ``b{foo}ar`` will be sotred in the same node.

.. note:: Hash Tags are not supported with ``bytes`` keys in Python 3.

Tag method
~~~~~~~~~~~

Just add ``tag_`` prefix, you can use any of the normal redis method on the same hash tag::

    client.tag_mget("{user:1}question1", "{user:1}question2")
    client.tag_delete("{user:1}question1", "{user:1}question2")


Multi-keys method
~~~~~~~~~~~~~~~~~~
Only support ``mget``, ``mset`` and ``flushdb``.


Config Details
--------------
There are three parameters ``servers``, ``hash_method`` and ``sentinel`` in the class `redis_shard.shard.RedisShardAPI`.

``servers`` is a list.  Each element in it should be a dict or a URL schema.

- dict::

    [
        {'name': 'server1', 'host': '127.0.0.1', 'port': 10000, 'db': 0},
        {'name': 'server2', 'host': '127.0.0.1', 'port': 11000, 'db': 0, 'max_connections': 50},
        {'name': 'server3', 'host': '127.0.0.1', 'port': 12000, 'db': 0},
    ]

- URL schema::

    [
        'redis://127.0.0.1:10000/0?name=node1',
        'redis://127.0.0.1:11000/0?name=node2&max_connections=50',
        'redis://127.0.0.1:12000/0?name=node3'
    ]

If the following parameter ``sentinel`` is enabled, only **name** is needed for the ``servers`` config.

``hash_method`` is a string which indicate the method of generating the hash key of the consistent hash ring.
The default value is **crc32**. It also supports **md5** and **sha1**.


``sentinel`` is the config for `Redis Sentinel <http://redis.io/topics/sentinel>`_. With the sentinel support, redis-shard
will do read/write splitting. Config is like this::

    {"hosts": [('localhost', 26379)], "socket_timeout": 0.1}



Limitations
===========

* Redis Shard dose not support all Redis commands.
* As mentioned above, Redis Shard does not support all multi-keys commands crossing different nodes,
  you have to use Hash Tag to work with those commands.
* Redis Shard does not have any replication mechanism.


How it Works
============

Redis Shard is basically inspired by `this article <http://oldblog.antirez.com/post/redis-presharding.html>`_.
