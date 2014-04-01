![Concentric Sky](https://concentricsky.com/media/uploads/images/csky_logo.jpg)

# Django Cache Model

Django Cache Model is an open-source Django library developed by [Concentric Sky](http://concentricsky.com/). It provides abstract Django models that perform caching using the "publish" method.


### Table of Contents
- [Version History](#version-history)
- [Why the Publish model?](#why-the-publish-model)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [License](#license)
- [About Concentric Sky](#about-concentric-sky)

## Version History

- v2.0.0 Library was converted to Publish model
- v0.9.8 Public codebase was released


## Why the Publish model?

Most cache schemes lazily fill a cache key after the first miss. The advantage of this is you don't have to manage values in the cache, you simply let requests populate it for you. You don't have to worry about cache invalidation, as stale values simply roll off after the timeout period expires. But what happens when many requests hit at the same time? Suddenly the database is processing the same request many times, and this can often overload a system. To avoid this thundering herd, we can instead have Model.save() call a self.publish() method which populates the cache with an infinite timeout. It automatically publishes indexes by _pk_ and provides a callback for the user to implement their own caches. The infinite cache timeout means the save() method is responsible for making sure the cache is never stale. But if we have control over when a model's data ever changes, the "publish" method is much more efficient than lazy schemes. And updates to the database will immediately be pushed to the cache and users will not have to wait for a timeout to see the latest updates.


## Installation

    pip install git+https://github.com/concentricsky/django-cachemodel.git


## Getting Started


In your models.py file:

```python

import cachemodel

class YourFancyModel(cachemodel.CacheModel):
    name = models.TextField()

    def publish(self):
        super(YourFancyModel, self).publish()
        self.publish_by("name", self.name)
```

Now whenever YourFancyModel.save() is called, two keys will be published to the cache that reference this object: `YourFancyModel:pk:<pk>` and `YourFancyModel:name:<name>`.

Cached copies can be retried by using the _.cached()_ manager.

```python
# hit the cache first, or fall back to db
cachedOrDbFancy = YourFancyModel.cached.get(pk=42)   

# lookup by our custom publish index:
cached = YourFancyModel.cached.get(name=42)

# Or, hit the db directly
fancy = YourFancyModel.objects.get(pk=42)

```


You can pass any number of arguments to _.cached.get()_ and they will all become part of the index.


## License

This project is licensed under the Apache License, Version 2.0. Details can be found in the LICENSE.md file.


## About Concentric Sky

_For nearly a decade, Concentric Sky has been building technology solutions that impact people everywhere. We work in the mobile, enterprise and web application spaces. Our team, based in Eugene Oregon, loves to solve complex problems. Concentric Sky believes in contributing back to our community and one of the ways we do that is by open sourcing our code on GitHub. Contact Concentric Sky at hello@concentricsky.com._
