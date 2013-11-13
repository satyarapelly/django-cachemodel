# Django Cache Model

Abstract Django Model for doing caching using the "publish" method.

To avoid the thundering herd problem of caching on lookup calls. Instead have Model.save call self.publish() which automatically publishes indexes by _pk_ and provides a callback for the user to implement their own caches.

## Usage


In your models.py file:

```python

import cachemodel

class YourFancyModel(cachemodel.CacheModel):
    name = models.TextField()

    def publish(self):
        super(YourFancyModel, self).publish()
        self.publish_by("name", self.name)
```

Now whenever YourFancyModel.save() is called, 2 keys will be published to the cache that reference this object: "YourFancyModel:pk:<pk>" and "YourFancyModel:name:<name>".

Cached copies can be retried by using the _.cached_ manager.

```python
# hit the cache first, or fall back to db
cachedOrDbFancy = YourFancyModel.cached.get(pk=42)   

# lookup by our custom publish index:
cached = YourFancyModel.cached.get(name=42)

# Or, hit the db directly
fancy = YourFancyModel.objects.get(pk=42)

```


You can pass any number of arguments to _.cached.get()_ and they will all become part of the index.