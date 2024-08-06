from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import Category, JobAd
from job_assistant.crawlers.scraper.scraper.spiders.dev_bg import DevBgSpider
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from bleach.sanitizer import Cleaner
import html


class Command(BaseCommand):
    help = "Crawl all JobAds from DevBgSpider. For initial DB population only !"

    def handle(self, *args, **options):
        results = []

        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        dispatcher.connect(crawler_results, signal=signals.item_passed)


        process = CrawlerProcess(get_project_settings())
        process.crawl(DevBgSpider)
        process.start()

        cleaner = Cleaner(tags=[], attributes=[], protocols=[], strip=True, strip_comments=True)
        for result in results:
            categories = handle_categories(result)
            clean_body(result, cleaner)

            ad = JobAd(**result)
            ad.save()

            ad.categories.add(*categories)


        # JobAd.objects.bulk_create(ads)


# TODO: Move these funcs to other file/ mby utils
def handle_categories(ad):
    category_names = ad.pop("categories")
    categories = []
    for name in category_names:
        category, created = Category.objects.get_or_create(name=name.strip())
        categories.append(category)
    return categories

def clean_body(ad, cleaner):
    body = cleaner.clean(ad["body"])
    body = html.unescape(body)
    ad["body"] = body
