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

from django.core.cache import cache
from django.db import models


CACHE_FOREVER_TIMEOUT=86400*365



class CacheModel(models.Model):
    """An abstract model that has convienence functions for dealing with caching."""
    objects = models.Manager()
    cached = CacheModelManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        #find all the denormalized fields and update them
        for method in find_fields_decorated_with(self, '_denormalized_field'):
            if hasattr(method, '_denormalized_field_name'):
                setattr(self, method._denormalized_field_name, method(self))

        # save ourselves to the database
        super(CacheModel, self).save(*args, **kwargs)

        # trigger cache publish
        self._real_publish()

    # def delete(self, *args, **kwargs):
    #     super(CacheModel, self).delete(*args, **kwargs)
    #     # trigger publish if we are deleted.
    #     self.publish()

    def _real_publish(self):
        # cache ourselves so that we're ready for .cached.get(pk=)
        key = generate_cache_key([self.__class__.__name__, "get"], pk=self.pk)
        cache.set(key, self, CACHE_FOREVER_TIMEOUT)

        # find any @cached_methods with auto_publish=True
        for method in find_fields_decorated_with(self, '_cached_method'):
            if not getattr(method, '_cached_method_auto_publish', False):
                continue
            try:
                # run the cached method and store it in cache
                key = generate_cache_key([self.__class__.__name__, method.__name__])
                value = method(self)
                cache.set(key, value, CACHE_FOREVER_TIMEOUT)
            except TypeError as e:
                # the @cached_method requires arguments, so we cant cache it automatically
                pass

        # call user hook
        self.publish()

    def publish(self):
        """User hook to publish to the cache"""
        pass




