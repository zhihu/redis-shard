#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 consistent hashing for nosql client
 based on ezmobius client (redis-rb)
 and see this article http://amix.dk/blog/viewEntry/19367
"""

import zlib
import bisect
from hashlib import md5, sha1

from ._compat import xrange, b, long


hash_methods = {
    'crc32': zlib.crc32,
    'md5': lambda x: long(md5(x).hexdigest(), 16),
    'sha1': lambda x: long(sha1(x).hexdigest(), 16),
}


class HashRing(object):

    """Consistent hash for nosql API"""

    def __init__(self, nodes=[], replicas=128, hash_method='crc32'):
        """Manages a hash ring.

        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
        replicas are required to improve the distribution.
        `hash_method` is the key generator method.
        """
        self.hash_method = hash_methods[hash_method]
        self.nodes = []
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for n in nodes:
            self.add_node(n)

    def add_node(self, node):
        """Adds a `node` to the hash ring (including a number of replicas).
        """
        self.nodes.append(node)
        for x in xrange(self.replicas):
            ring_key = self.hash_method(b("%s:%d" % (node, x)))
            self.ring[ring_key] = node
            self.sorted_keys.append(ring_key)

        self.sorted_keys.sort()

    def remove_node(self, node):
        """Removes `node` from the hash ring and its replicas.
        """
        self.nodes.remove(node)
        for x in xrange(self.replicas):
            ring_key = self.hash_method(b("%s:%d" % (node, x)))
            self.ring.pop(ring_key)
            self.sorted_keys.remove(ring_key)

    def get_node(self, key):
        """Given a string key a corresponding node in the hash ring is returned.

        If the hash ring is empty, `None` is returned.
        """
        n, i = self.get_node_pos(key)
        return n

    def get_node_pos(self, key):
        """Given a string key a corresponding node in the hash ring is returned
        along with it's position in the ring.

        If the hash ring is empty, (`None`, `None`) is returned.
        """
        if len(self.ring) == 0:
            return [None, None]
        crc = self.hash_method(b(key))
        idx = bisect.bisect(self.sorted_keys, crc)
        # prevents out of range index
        idx = min(idx, (self.replicas * len(self.nodes)) - 1)
        return [self.ring[self.sorted_keys[idx]], idx]

    def iter_nodes(self, key):
        """Given a string key it returns the nodes as a generator that can hold the key.
        """
        if len(self.ring) == 0:
            yield None, None
        node, pos = self.get_node_pos(key)
        for k in self.sorted_keys[pos:]:
            yield k, self.ring[k]

    def __call__(self, key):
        return self.get_node(key)
