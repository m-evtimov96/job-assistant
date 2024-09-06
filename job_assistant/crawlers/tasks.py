from celery import shared_task
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from job_assistant.crawlers.scraper.scraper.spiders.dev_bg import DevBgSpider
from job_assistant.crawlers.models import JobAd, Workplace
from job_assistant.crawlers.utils import handle_categories, handle_technologies, clean_body
from bleach.sanitizer import Cleaner
from datetime import datetime, timedelta, date
# from job_assistant import celery_app

# @celery_app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls every 30 minutes.
#     sender.add_periodic_task(crontab(minute="*/30"), add_tasks_from_elastic)

# @celery_app.task
# TODO: Schedule the tasks
@shared_task
def crawl_job_ads():
    "Crawl all JobAds from DevBgSpider. For initial DB population only !"
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

    return f"{len(results)} job ads crawled/scraped and saved to the database."


@shared_task
def crawl_job_ads_daily():
    "Crawl daily JobAds from DevBgSpider."
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    process = CrawlerProcess(get_project_settings())
    process.crawl(DevBgSpider, from_date=yesterday)
    process.start()

    cleaner = Cleaner(tags=[], attributes=[], protocols=[], strip=True, strip_comments=True)
    for result in results:
        categories = handle_categories(result)
        technologies = handle_technologies(result)
        workplace, created = Workplace.objects.get_or_create(name=result.pop("workplace").strip())

        clean_body(result, cleaner)

        ad = JobAd.all_objects.filter(url=result["url"])
        if ad:
            ad.update(**result)
            ad = ad[0]
            if ad.is_deleted:
                ad.restore()
            ad.categories.clear()
            ad.technologies.clear()
            ad.workplace = workplace
            ad.save()
        else:
            ad = JobAd(workplace=workplace, **result)
            ad.save()

        ad.categories.add(*categories)
        ad.technologies.add(*technologies)

    return f"{len(results)} job ads crawled/scraped and saved to the database."


@shared_task
def delete_expired_ads():
    "Delete expired job ads."
    expiry_date = date.today() - timedelta(days=29)
    expired_ads = JobAd.objects.filter(date__lte=expiry_date)
    count = expired_ads.count()
    expired_ads.delete()
    return(f"Soft deleted {count} expired ads.")
