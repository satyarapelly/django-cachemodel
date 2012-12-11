from django.core.cache import cache
from django.db import models
from cachemodel import CACHE_FOREVER_TIMEOUT
from cachemodel.utils import generate_cache_key


class CacheModelManager(models.Manager):
    def get(self, **kwargs):
        key = generate_cache_key([self.model.__class__.__name__, "get"], **kwargs)
        obj = cache.get(key)
        if obj is None:
            obj = super(CacheModelManager, self).get(**kwargs)
            cache.set(key, obj, CACHE_FOREVER_TIMEOUT)

            # update cache_key_index with obj.pk <- key
        return obj

    def get_by(self, *args, **kwargs):
        raise DeprecationWarning("get_by() has been deprecated, use .get() instead.")
        raise NotImplementedError

