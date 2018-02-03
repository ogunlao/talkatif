from .models import PostDebate
from discourse.models import Post

from datetime import date
today = date.today()

def site_processor(request):
    daily_posted_debate = PostDebate.published.all().filter(created__year=today.year, \
    created__month = today.month, created__day = today.day)
    daily_debate = daily_posted_debate.filter(debate_category="closed").count()
    daily_argument = daily_posted_debate.filter(debate_category="open").count()
    daily_discourse = Post.published.all().filter(created__year=today.year, \
    created__month = today.month, created__day = today.day).count()
    return {'daily_debate': daily_debate, 'daily_discourse':daily_discourse, 'daily_argument':daily_argument}
