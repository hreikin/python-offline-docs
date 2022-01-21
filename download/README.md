The crawler within the `download` folder scrapes the defined pages for 
links containing zip files. It then passes a list of the found items to 
the scrapy item pipeline for download.

### How To Run
Define the variables `allowed_domains` and `start_urls` within the file 
`file_download/spiders/get_files.py`.

Run the spider with the following command to start the scraper and send 
the found items to the scrapy pipeline. The `-O` flag outputs to file a 
jsonlines file containing information of what was found by the scraper.

```
scrapy crawl get_urls -O output.jl
```
