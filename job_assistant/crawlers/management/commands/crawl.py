from django.core.management.base import BaseCommand
from ....scraper.scraper.spiders.dev_bg import DevBgSpider
from scrapy.crawler import CrawlerProcess
from job_assistant.scraper.run_scraper import Scraper

from scrapy.utils.project import get_project_settings

class Command(BaseCommand):
    help = "Release the spiders"

    def handle(self, *args, **options):
        breakpoint()
        scraper = Scraper()
        scraper.run_spiders()

        # process = CrawlerProcess(get_project_settings())
        # process.crawl(DevBgSpider)
        # process.start()
