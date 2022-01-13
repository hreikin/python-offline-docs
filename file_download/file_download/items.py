# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FileDownloadItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class DownloadFilesItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field