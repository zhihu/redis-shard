#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from redis_shard.shard import RedisShardAPI
from nose.tools import eq_
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
        self.client.delete('test1')
        self.client.delete('test2')
        self.client.delete('test3')

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

    def test_mget(self):
        self.client.set('test1', 1)
        self.client.set('test2', 2)
        self.client.set('test3', 3)
        assert self.client.mget('test1', 'test2', 'test3') == ['1', '2', '3']

    def test_mset(self):
        self.client.mset({'test4': 4, 'test5': 5, 'test6': 6})
        eq_(self.client.get('test4'), '4')
        eq_(self.client.mget('test4', 'test5', 'test6'), ['4', '5', '6'])
