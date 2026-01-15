from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["homepage", "services", "about", "team", "contact"]

    def location(self, item):
        return reverse(item)
