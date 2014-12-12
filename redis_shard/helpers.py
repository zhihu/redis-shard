#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from .url import parse_url


def format_servers(servers):
    """
    :param servers: server list, element in it can have two kinds of format.

    - dict

    servers = [
        {'name':'node1','host':'127.0.0.1','port':10000,'db':0},
        {'name':'node2','host':'127.0.0.1','port':11000,'db':0},
        {'name':'node3','host':'127.0.0.1','port':12000,'db':0},
        ]


    - url_schema

    servers = ['redis://127.0.0.1:10000/0?name=node1',
                'redis://127.0.0.1:11000/0?name=node2',
                'redis://127.0.0.1:12000/0?name=node3'
        ]

    """
    configs = []
    if not isinstance(servers, list):
        raise ValueError("server's config must be list")
    _type = type(servers[0])
    if _type == dict:
        return servers
    if (sys.version_info[0] == 3 and _type in [str, bytes]) \
            or (sys.version_info[0] == 2 and _type in [str, unicode]):
        for config in servers:
            configs.append(parse_url(config))
    else:
        raise ValueError("invalid server config")
    return configs
