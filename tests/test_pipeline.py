#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from redis.exceptions import WatchError

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
        pipe.reset()
        eq_(self.client.get('test'), b'2')
        eq_(self.client.zscore('testzset', 'first'), 2.0)
        eq_(self.client.zscore('testzset', 'second'), 2.0)

        with self.client.pipeline() as pipe:
            pipe.set('test', '3')
            pipe.zadd('testzset', 'first', 4)
            pipe.zincrby('testzset', 'first')
            pipe.zadd('testzset', 'second', 5)
            pipe.execute()
        eq_(self.client.get('test'), b'3')
        eq_(self.client.zscore('testzset', 'first'), 5.0)
        eq_(self.client.zscore('testzset', 'second'), 5.0)

        with self.client.pipeline() as pipe:
            pipe.watch('test')
            pipe.incr('test')
            pipe.execute()
        eq_(self.client.get('test'), b'4')

        with self.client.pipeline() as pipe:
            pipe.watch('test')
            pipe.incr('test')
            self.client.decr('test')
            self.assertRaises(WatchError, pipe.execute)
        eq_(self.client.get('test'), b'3')

        keys_of_names = {}
        with self.client.pipeline() as pipe:
            for key in xrange(100):
                name = pipe.shard_api.get_server_name(key)
                if name not in keys_of_names:
                    keys_of_names[name] = key
                else:
                    key1 = key
                    key2 = keys_of_names[name]

                    pipe.watch(key1, key2)
                    pipe.set(key1, 1)
                    pipe.set(key2, 2)
                    pipe.execute()

                    eq_(self.client.get(key1), b'1')
                    eq_(self.client.get(key2), b'2')

    def test_pipeline_script(self):
        pipe = self.client.pipeline()
        for i in range(100):
            pipe.eval("""
                redis.call('set', KEYS[1], ARGV[1])
            """, 1, 'testx%d' % i, i)
        pipe.execute()
        for i in range(100):
            eq_(self.client.get('testx%d' % i), b('%d' % i))
