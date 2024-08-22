from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import JobAd
from job_assistant.crawlers.scraper.scraper.spiders.dev_bg import DevBgSpider
from job_assistant.crawlers.utils import handle_categories, clean_body
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from bleach.sanitizer import Cleaner
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Crawl daily JobAds from DevBgSpider."

    def handle(self, *args, **options):
        results = []

        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        dispatcher.connect(crawler_results, signal=signals.item_passed)

        # TODO: Check what date to use here
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        process = CrawlerProcess(get_project_settings())
        process.crawl(DevBgSpider, from_date=yesterday)
        process.start()

        cleaner = Cleaner(tags=[], attributes=[], protocols=[], strip=True, strip_comments=True)
        for result in results:
            categories = handle_categories(result)
            clean_body(result, cleaner)
            ad_exists = JobAd.all_objects.get(url=result["url"])
            # TODO: Check if ad allready exists (1/2 days old) or if exists but softdeleted and update/create accoridingly
            # TODO: Test this logic
            if ad_exists:
                if ad_exists.is_deleted:
                    ad_exists.restore()
                ad_exists.update(**result)
                ad_exists.categories.clear()
            else:
                ad = JobAd(**result)
                ad.save()
            ad.categories.add(*categories)
