# Scrapy Crawler
The crawler within the `download` folder scrapes the defined pages for 
links containing zip files. It then passes a list of the found items to 
the scrapy item pipeline for download.

By default the crawler is set to scrape the 2 archive pages for the Python docs 
and look for zip files. The downloaded files will be in 
`download/output` directory.

### How To Run
Define the variables `allowed_domains` and `start_urls` within the file 
`download/file_download/spiders/get_files.py`. You can optionally change the value of 
`FILES_STORE` in `download/file_download/settings.py` if you wish the files to be output 
elsewhere.

Run the spider with the following command to start the scraper and send 
the found items to the scrapy pipeline. The `-O` flag outputs to a 
jsonlines file information about what was found by the scraper.

```
scrapy crawl get_urls -O output.jl
```
