
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from job_assistant.crawlers.models import JobAd

# Run this job every day in the evening
class Command(BaseCommand):
    help = "Delete expired job ads."

    def handle(self, *args, **options):
        expiry_date = date.today() - timedelta(days=29)
        expired_ads = JobAd.objects.filter(date__lte=expiry_date)
        count = expired_ads.count()
        expired_ads.delete()
        print(f"Deleted {count} expired ads.")

