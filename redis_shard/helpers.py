#!/usr/bin/python
# -*- coding: utf-8 -*-
from .url import parse_url


def format_config(settings):
    """
    There's three config formats

    - list

    servers = [
        {'name':'node1','host':'127.0.0.1','port':10000,'db':0},
        {'name':'node2','host':'127.0.0.1','port':11000,'db':0},
        {'name':'node3','host':'127.0.0.1','port':12000,'db':0},
        ]

    - dict

    servers =
        { 'node1': {'host':'127.0.0.1','port':10000,'db':0},
            'node2': {'host':'127.0.0.1','port':11000,'db':0},
            'node3': {'host':'127.0.0.1','port':12000,'db':0},
        }

    - url_schema

    servers = ['redis://127.0.0.1:10000/0?name=node1',
                'redis://127.0.0.1:11000/0?name=node2',
                'redis://127.0.0.1:12000/0?name=node3'
        ]

    """
    configs = []
    if isinstance(settings, list):
        _type = type(settings[0])
        if _type == dict:
            return settings
        elif _type == str:
            for config in settings:
                configs.append(parse_url(config))
        else:
            raise ValueError("invalid server config")
    elif isinstance(settings, dict):
        for name, config in settings.items():
            config['name'] = name
            configs.append(config)
    else:
        raise ValueError("server's config must be list or dict")
    return configs
