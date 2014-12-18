#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from nose.tools import eq_
from redis_shard.shard import RedisShardAPI
from redis_shard._compat import b
from .config import settings


class TestShard(unittest.TestCase):

    def setUp(self):
        self.client = RedisShardAPI(**settings)
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

    def test_pipeline_script(self):
        pipe = self.client.pipeline()
        for i in range(100):
            pipe.eval("""
                redis.call('set', KEYS[1], ARGV[1])
            """, 1, 'testx%d' % i, i)
        pipe.execute()
        for i in range(100):
            eq_(self.client.get('testx%d' % i), b('%d' % i))
