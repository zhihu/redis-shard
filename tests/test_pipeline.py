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

    def test_pipeline(self):
        self.client.set('test', '1')
        pipe = self.client.pipeline()
        pipe.set('test', '2')
        pipe.zadd('testzset', 'first', 1)
        pipe.zincrby('testzset', 'first')
        pipe.zadd('testzset', 'second', 2)
        pipe.execute()
        self.client.get('test') == '2'
        self.client.zscore('testzset', 'fist') == '3.0'
