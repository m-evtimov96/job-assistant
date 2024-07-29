from scrapy_djangoitem import DjangoItem
from job_assistant.crawlers.models import JobAd


class JobAdItem(DjangoItem):
   django_model = JobAd
