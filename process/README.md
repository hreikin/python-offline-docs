# File Processing & Conversion
The scripts within the `process` folder unzip the files from the crawler 
before processing and extracting parts of the HTML using beautiful soup. 
The extracted HTML is used to create partials which are used with 
pandocs templating system to create the pages with pypandoc. Once the 
processing is complete the copied originals and partials are removed 
leaving the source HTML and converted versions separate.

### How To Run
While in development we just run the file directly to process the downloaded 
files into partials for use with pandocs templating system. Define the variables 
at the bottom of the page if you wish to change any of them and then run.

```
python3 making_soup.py
```
