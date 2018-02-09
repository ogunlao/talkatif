from django.utils import timezone
from django.contrib.auth.models import User
from haystack import indexes
from .models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    slug = indexes.CharField(model_attr='slug')
    summary = indexes.CharField(model_attr='summary')
    category = indexes.CharField(model_attr='category')
    author = indexes.CharField(model_attr='author')
    tags = indexes.MultiValueField(model_attr='tags__name', null=True)
    created = indexes.DateTimeField(model_attr='created', null=True)

    # def prepare_tags(self, object):
    #       return [tag.name for tag in object.tags.all()]

    def prepare_tags(self, object):
        tag_object = object.tags.all()
        if tag_object:
            return [tag.name for tag in tag_object]
        else:
            return None

    def prepare_author(self, object):
        if object.author:
            return object.author.get_full_name()
        else:
            return None

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
          return self.get_model().objects.filter(show = True)
