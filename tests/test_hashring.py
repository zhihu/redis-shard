#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_

from redis_shard.hashring import HashRing


class TestHashRing(unittest.TestCase):

    def test_remove_node(self):
        replicas = 128
        hash_ring_object = HashRing(
            nodes=["redis01", "redis02"],
            replicas=replicas,
            hash_method='md5',
        )
        hash_ring_object.remove_node("redis01")
        eq_(hash_ring_object.nodes, ["redis02"])
        eq_(list(hash_ring_object.ring.values()), ["redis02"] * replicas)
