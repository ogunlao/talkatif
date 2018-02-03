from django import template

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
