from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import Category, JobAd
from job_assistant.crawlers.scraper.scraper.spiders.dev_bg import DevBgSpider
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings

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
        # TODO: Add method for cleaning fields before saving to DB

        for result in results:
            categories = handle_categories(result)

            ad = JobAd(**result)
            ad.save()

            ad.categories.add(*categories)


        # JobAd.objects.bulk_create(ads)


# TODO: Move this to other file/ mby utils
def handle_categories(ad):
    categories = ad.pop("categories")
    categories_objects = [Category(name=category.strip()) for category in categories]
    ad_categories = Category.objects.bulk_create(categories_objects, update_conflicts=True, update_fields=['name'], unique_fields=['name'])

    return ad_categories
