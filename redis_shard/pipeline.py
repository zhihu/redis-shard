
import functools
import logging

from .commands import SHARD_METHODS
from ._compat import basestring, dictvalues


class Pipeline(object):

    def __init__(self, shard_api):
        self.shard_api = shard_api
        self.pipelines = {}
        self.__counter = 0
        self.__indexes = {}
        self.__watching = None
        self.shard_api._build_pool()

    def get_pipeline(self, key):
        name = self.shard_api.get_server_name(key)
        if name not in self.pipelines:
            self.pipelines[name] = self.shard_api.connections[name].pipeline()
        return self.pipelines[name]

    def __record_index(self, pipeline):
        if pipeline not in self.__indexes:
            self.__indexes[pipeline] = [self.__counter]
        else:
            self.__indexes[pipeline].append(self.__counter)
        self.__counter += 1

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        pipeline = self.get_pipeline(key)
        f = getattr(pipeline, method)
        r = f(*args, **kwargs)
        self.__record_index(pipeline)
        return r

    def __wrap_eval(self, method, script_or_sha, numkeys, *keys_and_args):
        if numkeys != 1:
            raise NotImplementedError("The key must be single string;mutiple keys cannot be sharded")
        key = keys_and_args[0]
        pipeline = self.get_pipeline(key)
        f = getattr(pipeline, method)
        r = f(script_or_sha, numkeys, *keys_and_args)
        self.__record_index(pipeline)
        return r

    def __wrap_tag(self, method, *args, **kwargs):
        key = args[0]
        if isinstance(key, basestring) and '{' in key:
            pipeline = self.get_pipeline(key)
        elif isinstance(key, list) and '{' in key[0]:
            pipeline = self.get_pipeline(key[0])
        else:
            raise ValueError("method '%s' requires tag key params as its arguments" % method)
        method = method.lstrip("tag_")
        f = getattr(pipeline, method)
        r = f(*args, **kwargs)
        self.__record_index(pipeline)
        return r

    def execute(self):
        try:
            if self.__watching:
                return self.pipelines[self.__watching].execute()
            else:
                results = []

                # Pipeline concurrently
                values = self.shard_api.pool.map(self.__unit_execute, dictvalues(self.pipelines))
                for v in values:
                    results.extend(v)

                self.__counter = 0
                self.__indexes = {}

                results.sort(key=lambda x: x[0])
                results = [r[1] for r in results]
                return results
        finally:
            self.reset()

    def __unit_execute(self, pipeline):
        result = pipeline.execute()
        return zip(self.__indexes.get(pipeline, []), result)

    def __getattr__(self, method):
        if method in SHARD_METHODS:
            return functools.partial(self.__wrap, method)
        elif method in ('eval', 'evalsha'):
            return functools.partial(self.__wrap_eval, method)
        elif method.startswith("tag_"):
            return functools.partial(self.__wrap_tag, method)
        else:
            raise NotImplementedError(
                "method '%s' cannot be pipelined" % method)

    def watch(self, *keys):
        if not keys:
            return

        watching_server_name = self.__watching
        if watching_server_name:
            for key in keys:
                name = self.shard_api.get_server_name(key)
                if watching_server_name != name:
                    raise ValueError('Cannot watch keys in different redis instances')
        else:
            for key in keys:
                name = self.shard_api.get_server_name(key)
                if watching_server_name is None:
                    watching_server_name = name
                elif watching_server_name != name:
                    raise ValueError('Cannot watch keys in different redis instances')

        pipeline = self.pipelines.get(watching_server_name)
        if not pipeline:
            pipeline = self.shard_api.connections[watching_server_name].pipeline()
            self.pipelines[watching_server_name] = pipeline
        r = pipeline.watch(*keys)
        self.__watching = watching_server_name
        return r

    def multi(self):
        if self.__watching:
            pipeline = self.pipelines[self.__watching]
            pipeline.multi()
        else:
            raise NotImplementedError('Cannot call MULTI in different redis instances')

    def reset(self):
        if self.__watching:
            pipeline = self.pipelines[self.__watching]
            try:
                pipeline.reset()
            except Exception:
                logging.warning('failed to reset pipeline')
            self.__watching = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset()

    def __del__(self):
        self.reset()
