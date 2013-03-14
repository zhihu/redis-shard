
import functools
from .commands import SHARD_METHODS


class Pipeline(object):
    def __init__(self, shard_api):
        self.shard_api = shard_api
        self.pipelines = {}

    def get_pipeline(self, key):
        name = self.shard_api.get_server_name(key)
        if name not in self.pipelines:
            self.pipelines[name] = self.shard_api.connections[name].pipeline()
        return self.pipelines[name]

    def __wrap(self, method, *args, **kwargs):
        try:
            key = args[0]
            assert isinstance(key, basestring)
        except:
            raise ValueError("method '%s' requires a key param as the first argument" % method)
        pipeline = self.get_pipeline(key)
        f = getattr(pipeline, method)
        return f(*args, **kwargs)

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
        return f(*args, **kwargs)

    def execute(self):
        results = []
        for name, pipeline in self.pipelines.iteritems():
            result = pipeline.execute()
            results.extend(list(result))
        return results

    def __getattr__(self, method):
        if method in SHARD_METHODS:
            return functools.partial(self.__wrap, method)
        elif method.startswith("tag_"):
            return functools.partial(self.__wrap_tag, method)
        else:
            raise NotImplementedError(
                "method '%s' cannot be pipelined" % method)
