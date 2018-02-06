from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from debate.models import PostDebate
from discourse.models import Post

class PostDebateSitemap(Sitemap):
    """
    Sitemaps for all debate pages.
    """
    changefreq = 'always'
    priority = 0.5

    def items(self):
        return PostDebate.published.all()

    def lastmod(self, obj):
        return obj.updated

class PostSitemap(Sitemap):
    """
    Sitemaps for all discourse pages.
    """
    changefreq = 'always'
    priority = 0.5

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated

class StaticViewSitemap(Sitemap):
    """
    Sitemaps for static pages e.g index page, faq
    """
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['main_page', 'faq']

    def location(self, item):
        return reverse(item)
