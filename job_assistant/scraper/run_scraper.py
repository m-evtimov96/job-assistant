from job_assistant.scraper.scraper.spiders.dev_bg import DevBgSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os


class Scraper:
    def __init__(self):
        settings_file_path = 'job_assistant.scraper.scraper.settings' # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = DevBgSpider # The spider you want to crawl

    def run_spiders(self):
        breakpoint()
        self.process.crawl(self.spider)
        self.process.start()  # the script will block here until the crawling is finished