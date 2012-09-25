#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from redis_shard.shard import RedisShardAPI
from .config import servers


class TestShard(unittest.TestCase):

    def setUp(self):
        self.client = RedisShardAPI(servers)
        self.clear_db()

    def tearDown(self):
        pass

    def clear_db(self):
        self.client.delete('testset')
        self.client.delete('testzset')
        self.client.delete('testlist')

    def test_zset(self):
        self.client.zadd('testzset', 'first', 1)
        self.client.zadd('testzset', 'second', 2)
        self.client.zrange('testzset', 0, -1) == ['first', 'second']

    def test_list(self):
        self.client.rpush('testlist', 0)
        self.client.rpush('testlist', 1)
        self.client.rpush('testlist', 2)
        self.client.rpush('testlist', 3)
        self.client.rpop('testlist')
        self.client.lpop('testlist')
        self.client.lrange('testlist', 0, -1) == ['1', '2']
