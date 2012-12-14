
from django.db import models
import cachemodel

import datetime



# class Category(cachemodel.CachedTable):
#     slug = models.SlugField()
#     name = models.TextField()



class Author(cachemodel.CacheModel):
    first_name = models.TextField()
    last_name = models.TextField()
    bio = models.TextField()

    # this is to test @cached_method with auto_publish=True
    @cachemodel.cached_method(auto_publish=True)
    def num_posts(self):
        return self.post_set.all().count()

    def publish(self):
        super(Author, self).publish()
        self.publish_by('first_name','last_name')



class Post(cachemodel.CacheModel):
    title = models.TextField()
    author = models.ForeignKey(Author)
    body = models.TextField()
    popularity = models.IntegerField(default=0)
    # category = models.ForeignKey(Category)

    # this is to test a child model triggering publishing/denormalizing on a parent
    def publish(self):
        super(Post, self).publish()
        self.author.publish()

    # this is so we can test @denormalized_field
    @cachemodel.denormalized_field('popularity')
    def _popularity(self):
        return self.comment_set.all().count()

    # this is so we can test @cached_method with parens but no arguments.
    @cachemodel.cached_method()
    def last_comments(self, how_many=3):
        return self.comment_set.all().order_by('-created_at')[:how_many]



class Comment(cachemodel.CacheModel):
    post = models.ForeignKey(Post)
    user = models.ForeignKey("auth.User")
    comment = models.TextField()
    parent = models.ForeignKey("self", related_name='children', null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)

    # this is to test a child model triggering publishing/denormalizing on a parent
    def publish(self):
        super(Comment, self).publish()
        self.post.publish()

    # this is to test @cached_method with no parens
    @cachemodel.cached_method
    def replies(self):
        return Comment.objects.filter(parent=self)




