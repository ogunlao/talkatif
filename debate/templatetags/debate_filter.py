from django import template
from django.conf import settings

register = template.Library()

# @register.filter()
# def for_names(things, names):
#     return things.filter(person=names).filter(won = True).count()

@register.filter()
def where_won(things, names):
    return things.filter(person=names).filter(won = True).count()

@register.filter()
def where_lost(things, names):
    return things.filter(person=names).filter(lost = True).count()

@register.filter()
def minute_read(text):
    time_in_mins = getReadingTime(text)
    return str(time_in_mins) +" minues read."


def getReadingTime(content):
    """"Calculate the amount of time needed to read a tet in minutes"""
    wpm = 180 #readable words per minutes
    word_length = 5 #standardized number of chars in calculabe words
    words = len(content)/word_length
    words_time = words/wpm
    words_time = round(words_time,2)

    return words_time

import requests
import json
API_KEY = settings.GOO_API_KEY
@register.filter()
def goo_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(API_KEY)
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    print(r.json())
    try:
        return r.json()["id"]
    except:
        return url
