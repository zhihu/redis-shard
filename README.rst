Redis Shard 
==============
A redis sharding api. Sharding is done based on the CRC32 checksum of a key or key tag ("key{key_tag}"),
according to this article http://antirez.com/post/redis-presharding.html .
