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
