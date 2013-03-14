#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from redis_shard.shard import RedisShardAPI

old_servers = [{'name': 'feed1', 'host': 'feedproxy', 'port': 6301, 'db': 0},
               {'name': 'feed2', 'host': 'feedproxy', 'port': 6302, 'db': 0},
               {'name': 'feed3', 'host': 'feedproxy', 'port': 6303, 'db': 0},
               {'name': 'feed4', 'host': 'feedproxy', 'port': 6304, 'db': 0},
               {'name': 'feed5', 'host': 'feedproxy', 'port': 6305, 'db': 0},
               {'name': 'feed6', 'host': 'feedproxy', 'port': 6306, 'db': 0},
               {'name': 'feed7', 'host': 'feedproxy', 'port': 6307, 'db': 0},
               {'name': 'feed8', 'host': 'feedproxy', 'port': 6308, 'db': 0},
               {'name': 'feed9', 'host': 'feedproxy', 'port': 6309, 'db': 0},
               {'name': 'feed10', 'host': 'feedproxy', 'port': 6310, 'db': 0},
               ]

new_servers = [{'name': 'feed1', 'host': 'feedproxy', 'port': 6301, 'db': 0},
               {'name': 'feed2', 'host': 'feedproxy', 'port': 6302, 'db': 0},
               {'name': 'feed3', 'host': 'feedproxy', 'port': 6303, 'db': 0},
               {'name': 'feed4', 'host': 'feedproxy', 'port': 6304, 'db': 0},
               {'name': 'feed5', 'host': 'feedproxy', 'port': 6305, 'db': 0},
               {'name': 'feed6', 'host': 'feedproxy', 'port': 6306, 'db': 0},
               {'name': 'feed7', 'host': 'feedproxy', 'port': 6307, 'db': 0},
               {'name': 'feed8', 'host': 'feedproxy', 'port': 6308, 'db': 0},
               {'name': 'feed9', 'host': 'feedproxy', 'port': 6309, 'db': 0},
               {'name': 'feed10', 'host': 'feedproxy', 'port': 6310, 'db': 0},
               {'name': 'feed11', 'host': 'feedproxy', 'port': 6311, 'db': 0},
               {'name': 'feed12', 'host': 'feedproxy', 'port': 6312, 'db': 0},
               {'name': 'feed13', 'host': 'feedproxy', 'port': 6313, 'db': 0},
               {'name': 'feed14', 'host': 'feedproxy', 'port': 6314, 'db': 0},
               {'name': 'feed15', 'host': 'feedproxy', 'port': 6315, 'db': 0},
               {'name': 'feed16', 'host': 'feedproxy', 'port': 6316, 'db': 0},
               {'name': 'feed17', 'host': 'feedproxy', 'port': 6317, 'db': 0},
               {'name': 'feed18', 'host': 'feedproxy', 'port': 6318, 'db': 0},
               {'name': 'feed19', 'host': 'feedproxy', 'port': 6319, 'db': 0},
               {'name': 'feed20', 'host': 'feedproxy', 'port': 6320, 'db': 0},
               ]


FEED_KEY = "{feed%(user_id)s}:list"

old_shard = RedisShardAPI(old_servers)
new_shard = RedisShardAPI(new_servers)


def main():
    parser = argparse.ArgumentParser(description='Reshard newsfeed instance')
    parser.add_argument(
        '--start', type=int, required=True, help='start user id')
    parser.add_argument('--end', type=int, required=True, help='start user id')
    parser.add_argument('--show_only', type=bool, default=False,
                        help='only showw migrate process')
    parser.add_argument(
        '--delete', type=bool, default=False, help='real delete old data')
    args = parser.parse_args()
    migrate(args.start, args.end, args.delete, args.show_only)


def migrate(start, end, delete, show_only=False):
    for user_id in range(start, end):
        feed_list_key = FEED_KEY % dict(user_id=user_id)
        old_server_name = old_shard.get_server_name(feed_list_key)
        new_server_name = new_shard.get_server_name(feed_list_key)
        if old_server_name != new_server_name:
            print "%s : %s => %s" % (user_id, old_server_name, new_server_name)
            if show_only:
                continue
            old_server = old_shard.get_server(feed_list_key)
            new_server = new_shard.get_server(feed_list_key)
            if not delete:
                for k, v in old_server.zrange(feed_list_key, 0, -1, withscores=True):
                    new_server.zadd(feed_list_key, k, v)
            else:
                old_server.delete(feed_list_key)

if __name__ == '__main__':
    main()
