from django.core.management.base import BaseCommand
from job_assistant.crawlers.tasks import crawl_job_ads_daily

class Command(BaseCommand):
    help = "Run the celery task to crawl daily JobAds from DevBgSpider."

    def handle(self, *args, **options):
        result = crawl_job_ads_daily.delay()
        self.stdout.write(self.style.SUCCESS(f"Task {result.id} for daily crawling has been triggered successfully."))
