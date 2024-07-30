from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import JobAd
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
        JobAd.objects.bulk_create(
            [
                JobAd(**result)
                for result in results
            ]
        )