#  Copyright 2010 Concentric Sky, Inc. 
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from django.conf import settings
from django.core.cache import cache
from django.db import models
from cachemodel import ns_cache
import datetime

class CacheModelManager(models.Manager):
    """Manager for use with CacheModel"""
    def get_by(self, field_name, field_value, cache_timeout=None):
        """A convienence function for looking up an object by a particular field

        If the object is in the cache, returned the cached version.
        If the object is not in the cache, do a basic .get() call and store it in the cache.

        Fields used for lookup will be stored in the special cache, '__cached_field_names__'
        so they can be automatically purged on the object's flush_cache() method
        """
        if cache_timeout is None:
            cache_timeout = getattr(settings, 'CACHE_TIMEOUT', 900)

        # cache the field name that was used so flush_cache can purge them automatically
        cached_field_names = cache.get( self.model.cache_key("__cached_field_names__") )
        if cached_field_names is None:
            cached_field_names = set()
        cached_field_names.add(field_name)
        cache.set(self.model.cache_key("__cached_field_names__"), cached_field_names, cache_timeout)
        key = self.model.cache_key("by_"+field_name, field_value)
        obj = cache.get(key)
        if obj is None:
            obj = self.get(**{field_name: field_value})
            cache.set(key, obj, cache_timeout)
        return obj

    def get_by_pk(self, pk, cache_timeout=None):
        """Convienence function that calls get_by("pk", value)"""
        return self.get_by("pk",pk)


class CacheModel(models.Model):
    """An abstract model that has convienence functions for dealing with caching."""
    objects = CacheModelManager()
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(CacheModel, self).save(*args, **kwargs)
        self.flush_cache()
    def delete(self, *args, **kwargs):
        super(CacheModel, self).delete(*args, **kwargs)
        self.flush_cache()
    def flush_cache(self):
        """this method is called on save() and delete(), any cached fields should be expunged here."""
        #lookup the fields that have been cached by .get_by() and purge them
        cached_field_names = cache.get( self.cache_key("__cached_field_names__") ) 
        if cached_field_names is not None:
            for field_name in cached_field_names:
                cache.delete( self.cache_key("by_"+field_name, getattr(self, field_name)) )
        self.ns_flush_cache()
    def ns_cache_key(self, *args):
        """Return a cache key inside the object's namespace.

        The namespace is built from: The Objects class.__name__ and the Object's PK.
        """
        return ns_cache.ns_key(self.cache_key(self.pk), args)
    def ns_flush_cache(self):   
        """Flush all cache keys inside the object's namespace"""
        ns_cache.ns_flush(self.cache_key(self.pk))

    @classmethod
    def cache_key(cls, *args):
        """Generate a cache key from the object's class.__name__ and the arguments given"""
        key = cls.__name__
        for arg in args:
            key += '_'+str(arg)
        return key


def cached_method(cache_timeout, cache_key):
    """A decorator for CacheModel methods.

     - Builds a key based on cache_key and the object's ns_cache_key() method.
     - Checks the cache for data at that key, if data exists it is returned and the method is never called.
     - If the cache is stale or nonexistent, run the method and cache the result at the key specifieid.

    Arguments:
      cache_timeout -- the number of seconds to keep the cached data
      cache_key -- a key for the cached method, it will be inside the object's namespace via CacheModel.ns_cache_key()

    """
    def decorator(target):
        def wrapper(self, *args, **kwargs):
            key = self.ns_cache_key(cache_key)
            chunk = cache.get(key)
            if chunk is None:
                chunk = target(self, *args, **kwargs)
                cache.set(key, chunk, cache_timeout)
            return chunk
        return wrapper
    return decorator
