# Scrapy Crawler
The crawler within the `file_download` folder scrapes the defined pages for 
links containing zip files. It then passes a list of the found items to 
the scrapy item pipeline for download.

By default the crawler is set to scrape the 2 archive pages for the Python docs 
and look for zip files. The downloaded files will be in 
`src` directory.

### How To Run
Define the variables `allowed_domains` and `start_urls` within the file 
`build/file_download/spiders/get_files.py`. You can optionally change the value of 
`FILES_STORE` in `build/file_download/settings.py` if you wish the files to be output 
elsewhere.

Run the spider with the following command to start the scraper and send 
the found items to the scrapy pipeline. The `-O` flag outputs to a 
jsonlines file information about what was found by the scraper.

```
scrapy crawl get_files -O output.jl
```

# File Processing & Conversion
The scripts within this folder unzip the files from the crawler 
before processing and extracting parts of the HTML using beautiful soup. 
The extracted HTML is used to create partials which are used with 
pandocs templating system to create the pages with pypandoc.

### How To Run
While in development, run the file directly to process the downloaded 
files into partials for use with pandocs templating system. Define the 
variables at the bottom of the page if you wish to change any of them 
and then run.

```
python3 making_soup.py
```
