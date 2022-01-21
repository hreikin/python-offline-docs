# Python Offline Docs
This project utilizes scrapy, beautiful soup, pypandoc and pywebview to 
create an offline Material Design themed version of the official Python 
docs.

## Current Status
This app is currently a work in progress and in development. Work is 
currently focused on refining the extraction and styling of the final 
docs before an initial 0.1 release.

## How It Works
### Download
The crawler within the `download` folder scrapes the defined pages for 
links containing zip files. It then passes a list of the found items to 
the scrapy item pipeline for download.

### Process
The scripts within the `process` folder unzip the files from the crawler 
before processing and extracting parts of the HTML using beautiful soup. 
The extracted HTML is used to create partials which are used with 
pandocs templating system to create the pages. Once the processing is 
complete the copied originals and partials are removed leaving the 
source HTML and converted versions separate.

### App
The scripts within the `app` folder use pywebview to render the 
converted version of the docs. This folder will soon become its own 
repository to keep the app and build process separate.