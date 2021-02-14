#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from redis_shard.shard import RedisShardAPI, _PYTHON3
from redis_shard._compat import b
from nose.tools import eq_
from .config import settings


class TestTag(unittest.TestCase):

    def setUp(self):
        self.client = RedisShardAPI(**settings)

    def tearDown(self):
        pass

    def test_server_name(self):
        eq_(self.client.get_server_name('bar'), 'node1')
        eq_(self.client.get_server_name('c{bar}'), 'node1')
        eq_(self.client.get_server_name('c{bar}d'), 'node1')
        eq_(self.client.get_server_name('c{bar}e'), 'node1')
        eq_(self.client.get_server_name('d{bar}f'), 'node1')
        if _PYTHON3:
            eq_(self.client.get_server_name(b'd{bar}f'), 'node3')
        else:
            eq_(self.client.get_server_name(b'd{bar}f'), 'node1')
