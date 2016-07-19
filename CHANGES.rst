0.3.4 (2016-07-19)
------------------
- fix md5 hash_method occus NameError on python3

0.3.3 (2016-03-18)
-------------------
- max_connections can now be set when instantiating client instance, and has a default value 100.

0.3.2 (2015-06-02)
--------------------
- add strict redis support

0.3.1 (2015-02-02)
------------------
- transaction support

0.3.0 (2014-11-20)
------------------
- shard key generate function now support **md5** and **sha1** .
- add Redis Sentinel support

0.2.4 (2014-06-26)
------------------
- remove gevent dependency

0.2.3 (2014-06-02)
------------------
- better pipeline support

0.2.1 (2013-08-07)
------------------
- add evel method

0.2.0 (2013-06-02)
------------------
- add python3 support

0.1.11 (2013-05-06)
-------------------
- add mset support

0.1.10 (2013-04-13)
-------------------
- add mget support ,thks to @Yuekui

0.1.9 (2013-03-04)
------------------
- add an reshard example
- tidy the pipeline code
- add more shard methods

0.1.8 (2013-01-21)
------------------
- add `append` and `getrange` method, thks @simon-liu

0.1.7 (2012-11-19)
------------------
- use new redis url config instead of dict

0.1.5 (2012-07-16)
------------------
- Add many new methods, support socket_timeout and password

0.1.4 (2011-07-20)
------------------
- modify hash key algor, support suffix match, thks to dkong
- support more redis methods, include `keys`.

0.1.3 (2011-06-20)
------------------
- support 2.4.X version of redis-py

0.1.2 (2011-06-01)
------------------
- add MANIFEST.in file

0.1.1 (2011-05-29)
------------------
- create hashring use server's name config.

0.1 (2011-05-28)
----------------
- first version
