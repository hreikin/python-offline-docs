import scrapy
from scrapy.crawler import CrawlerProcess
from file_download.items import DownloadFilesItem

class GetFilesSpider(scrapy.Spider):
    name = 'get_files'
    allowed_domains = []
    start_urls = []

    def parse(self, response):
        for link in response.xpath('/html/body/pre/a'):
            all_url = response.url + link.xpath('.//@href').get()
            allowed = 'html.zip'
            if allowed in all_url:
                url = response.urljoin(all_url)
                item = DownloadFilesItem()
                item['file_urls'] = [url]
                yield item

def run_spider():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "output/output.jl": {"format": "jl"},
        },
    })
    domain = input("Enter the domain, e.g. example.com and press enter: ")
    url_to_add = input("Enter the URL, e.g. https://example.com/ and press enter: ")
    process.crawl(GetFilesSpider, start_urls = [url_to_add], allowed_domains = [domain])
    process.start() # the script will block here until the crawling is finished
    print("\n\n\n")
    input("Crawling finished. Press any key to return to the menu: ")