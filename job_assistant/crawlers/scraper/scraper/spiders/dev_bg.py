import scrapy

from ..items import JobAdItem


class DevBgSpider(scrapy.Spider):
    name = "dev_bg"
    allowed_domains = ["dev.bg"]
    start_urls = ["https://dev.bg/?s=&post_type=job_listing"]

    def parse(self, response):
        jobs_links = response.xpath('//div[@class="inner-right listing-content-wrap"]/a/@href').getall()
        yield from response.follow_all(jobs_links, self.parse_jobs)

        next_page = response.xpath('//div[@class="paggination-holder"]//a[@href]').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_jobs(self, response):
        # TODO Change xpaths to use contains, so it does not brake when there are more classes
        title = response.xpath('//h1[@class="job-title ab-title-placeholder ab-cb-title-placeholder"]/text()').get().strip()
        body = response.xpath('//div[@class="job_description"]').get()
        date = response.xpath('//time/@datetime').get()
        company = response.xpath('//span[@class="company-name  "]/text()').get()
        categories = response.xpath('//div[@class="categories-wrap"]/a/text()').getall() #TODO: this saves only yhe first el of the list
        # techstack = response.xpath('//img[@class="attachment-medium size-medium"]/@title').getall()
        url = response.url

        item = JobAdItem()
        item['title'] = title
        item['body'] = body
        item['date'] = date
        item['company'] = company
        item['categories'] = categories
        # TODO: Techstack does not work - Keyerror ?
        # item['techstack'] = techstack
        item['url'] = url

        yield item