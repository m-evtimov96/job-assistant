import scrapy
from datetime import datetime


from ..items import JobAdItem


class DevBgSpider(scrapy.Spider):
    name = "dev_bg"
    allowed_domains = ["dev.bg"]
    start_urls = ["https://dev.bg/?s=&post_type=job_listing"]

    def __init__(self, from_date=None, *args, **kwargs):
        super(DevBgSpider, self).__init__(*args, **kwargs)
        self.from_date = from_date
        if self.from_date:
            self.from_date = datetime.strptime(self.from_date, '%Y-%m-%d')
        self.continue_crawling = True

    def parse(self, response):
        if not self.continue_crawling:
            return
        
        jobs_links = response.xpath('//div[@class="inner-right listing-content-wrap"]/a/@href').getall()
        yield from response.follow_all(jobs_links, self.parse_jobs)

        if self.continue_crawling:
            next_page = response.xpath('//div[@class="paggination-holder"]//a[@class="next page-numbers"]/@href').get()
            if next_page:
                yield response.follow(next_page, self.parse)

    def parse_jobs(self, response):
        date = response.xpath('//time/@datetime').get()
        job_date = datetime.strptime(date, '%Y-%m-%d')
        if self.from_date and job_date < self.from_date:
            self.continue_crawling = False
            return

        # TODO Change xpaths to use contains, so it does not brake when there are more classes
        title = response.xpath('//h1[@class="job-title ab-title-placeholder ab-cb-title-placeholder"]/text()').get().strip()
        body = response.xpath('//div[@class="job_description"]').get() #TODO: this can be empty if custom js is used
        if not body:
            iframe_src = response.xpath('//iframe[@id="custom-job-design"]/@src').get()
            body = self.parse_body_iframe(iframe_src)
        company = response.xpath('//span[@class="company-name  "]/text()').get()
        categories = response.xpath('//div[@class="categories-wrap"]/a/text()').getall()
        technologies = response.xpath('//img[@class="attachment-medium size-medium"]/@title').getall()
        fully_remote = response.xpath('//span[contains(@class, "remote") and contains(@class, "bold")]').get()
        city_hybrid = response.xpath('//span[contains(@class, "hybrid")]/a/text()').get()
        if fully_remote:
            workplace = "Fully Remote"
        elif city_hybrid:
            workplace = f"{city_hybrid.strip()} - Hybrid"
        else:
            workplace = response.xpath('//div[@class="tags-wrap"]/a/span/text()').getall()[1].strip()
        url = response.url

        item = JobAdItem()
        item['title'] = title
        item['body'] = body
        item['date'] = date
        item['company'] = company
        item['categories'] = categories
        item['technologies'] = technologies
        item['workplace'] = workplace
        item['url'] = url

        yield item

    def parse_body_iframe(self, src):
        # TODO: Get body from src
        return src