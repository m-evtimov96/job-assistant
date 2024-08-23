from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import JobAd, Workplace
from job_assistant.crawlers.utils import handle_categories, handle_technologies, clean_body
from job_assistant.crawlers.scraper.scraper.spiders.dev_bg import DevBgSpider
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from bleach.sanitizer import Cleaner


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
            technologies = handle_technologies(result)
            workplace, created = Workplace.objects.get_or_create(name=result.pop("workplace").strip())

            clean_body(result, cleaner)

            ad = JobAd(workplace=workplace, **result)
            ad.save()

            ad.categories.add(*categories)
            ad.technologies.add(*technologies)
