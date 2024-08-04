from scrapy_djangoitem import DjangoItem
from job_assistant.crawlers.models import JobAd
import scrapy


class JobAdItem(DjangoItem):
   django_model = JobAd
   categories = scrapy.Field()
