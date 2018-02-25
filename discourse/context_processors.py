
from .models import Post

from datetime import date
today = date.today()

def site_processor(request):
    daily_talk = Post.published.all().filter(created__year=today.year, \
    created__month = today.month, created__day = today.day).count()
    return {'daily_talk':daily_talk}
