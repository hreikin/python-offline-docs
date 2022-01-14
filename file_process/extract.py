from pathlib import Path
import zipfile, os
import markdownify
from bs4 import BeautifulSoup

zipped_source = "/home/hreikin/git/python-offline-docs/file_download/output/downloads/full"
unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/src/"

def unzip_source(source_path, output_path):
    os.chdir(source_path)
    for file in os.listdir(source_path):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as item:
                item.extractall(output_path)

def convert_to_markdown(unzipped_source):
    for root, dirnames, filenames in os.walk(unzipped_source):
        for filename in filenames:
            if filename.endswith('.html'):
                fname = os.path.join(root, filename)
                mdname = root + "/" + filename.replace(".html", ".md")
                print(f'Opening HTML File: {fname}')
                with open(fname) as handle:
                    soup = BeautifulSoup(handle.read(), 'html.parser')
                    body_html = str(soup.find("div", class_="body"))
                    body_markdown = markdownify.markdownify(body_html)
                print(f'Creating Markdown File: {mdname}')
                with open(Path(mdname, exist_ok=True), "w") as stream:
                    stream.write(body_markdown)


# unzip_source(zipped_source, unzipped_source)
convert_to_markdown(unzipped_source)