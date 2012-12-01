Redis Shard 
==============
A redis sharding api. Sharding is done based on the CRC32 checksum of a key or key tag ("key{key_tag}"),
according to this article http://antirez.com/post/redis-presharding.html .

The source code is locate at `github <https://github.com/youngking/redis-shard>`_ .

Usage
==============
Creating a hash ring with multiple servers,By default the hash ring uses a crc32
hashing algorithm on the server's ``name`` config.You can define the name anything
as you like,but it must be unique.

I don't want to bind the hashring with ipaddress,because if I do some master/slave switches,
I can only change the ipaddress related config. The ``name`` is kept,so the hashring's order
is kept.

>>> from redis_shard.shard import RedisShardAPI
>>> servers = [
    ...    {'name':'server1','host':'127.0.0.1','port':10000,'db':0},
    ...    {'name':'server2','host':'127.0.0.1','port':11000,'db':0},
    ...    {'name':'server3','host':'127.0.0.1','port':12000,'db':0},
    ...    {'name':'127.0.0.1:13000','host':'127.0.0.1','port':13000,'db':0},
    ...    ]
>>> 
>>> client = RedisShardAPI(servers)
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
>>> client.set('{foo}d',5)
>>> client.set('d{foo}e',5)
>>> print client.get_server_name('foo') == client.get_server_name('a{foo}') == client.get_server_name('{foo}d') \
... == client.get_server_name('d{foo}e')

I also added an `tag_keys` method,which is more quickly than default `keys` method,because it only look 
one machine.

>>> client.tag_keys('*{foo}*') == client.keys('*{foo}*')

Config Format
-------------------

There's three config formats

- list::

 servers = [
       {'name':'node1','host':'127.0.0.1','port':10000,'db':0},
       {'name':'node2','host':'127.0.0.1','port':11000,'db':0},
       {'name':'node3','host':'127.0.0.1','port':12000,'db':0},
       ]

- dict::

 servers = 
       { 'node1': {'host':'127.0.0.1','port':10000,'db':0},
         'node2': {'host':'127.0.0.1','port':11000,'db':0},
         'node3': {'host':'127.0.0.1','port':12000,'db':0},
       }

- url_schema::

  servers = ['redis://127.0.0.1:10000/0?name=node1',
             'redis://127.0.0.1:11000/0?name=node2',
             'redis://127.0.0.1:12000/0?name=node3'
      ]


