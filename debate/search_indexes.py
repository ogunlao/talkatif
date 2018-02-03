from django.utils import timezone
from django.contrib.auth.models import User
from haystack import indexes
from .models import PostDebate


class PostDebateIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    slug = indexes.CharField(model_attr='slug')
    summary = indexes.CharField(model_attr='summary')
    debate_category = indexes.CharField(model_attr='debate_category')
    begin = indexes.DateTimeField(model_attr='begin',null=True)
    end = indexes.DateTimeField(model_attr='end', null=True)
    status = indexes.CharField(model_attr='status')
    author = indexes.CharField(model_attr='author')
    tags = indexes.MultiValueField(model_attr='tags__name', null=True)
    supporting_debaters = indexes.MultiValueField(null=True)
    #supporting_debaters = indexes.MultiValueField(model_attr='supporting_debaters__username')
    opposing_debaters = indexes.MultiValueField(null=True)
    #opposing_debaters = indexes.MultiValueField(model_attr='opposing_debaters__username')
    winner = indexes.CharField(model_attr='winner', null=True)

    # def prepare_tags(self, object):
    #       return [tag.name for tag in object.tags.all()]
    #
    def prepare_supporting_debaters(self, object):
        support_debaters = object.supporting_debaters.all()
        if support_debaters:
            return [debater.get_full_name() for debater in support_debaters]
        else:
            return None

    def prepare_opposing_debaters(self, object):
        oppose_debaters = object.opposing_debaters.all()
        if oppose_debaters:
            return [debater.get_full_name() for debater in oppose_debaters]
        else:
            return None

    def prepare_author(self, object):
        if object.author:
            return object.author.get_full_name()
        else:
            return None

    def prepare_begin(self, object):
        if object.begin:
            return object.begin
        else:
            return None

    def prepare_end(self, object):
        if object.end:
            return object.end
        else:
            return None

    def prepare_vote(self, object):
        if object.vote:
            return object.vote
        else:
            return None
    def prepare_winner(self, object):
        if object.winner:
            return object.winner
        else:
            return None

    def prepare_tags(self, object):
        tag_object = object.tags.all()
        if tag_object:
            return [tag for tag in tag_object]
        else:
            return None

    def get_model(self):
        return PostDebate
    def index_queryset(self, using=None):
          return self.get_model().objects.filter(show = True)
