from pathlib import Path
import zipfile, os, shutil
import markdownify
from bs4 import BeautifulSoup

zipped_source = "/home/hreikin/git/python-offline-docs/file_download/output/downloads/full"
unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/src/"
markdown_path = "/home/hreikin/git/python-offline-docs/file_process/output/converted/"

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

def move_markdown(source_path, target_path):
    src = Path(source_path, exist_ok=True)
    trg = Path(target_path, exist_ok=True)
    for root, dirnames, filenames in os.walk(src):
        for filename in filenames:
            if filename.endswith('.md'):
                fpath = os.path.join(root, filename)
                dir_path = Path(fpath.replace("src", "converted").rstrip(filename), exist_ok=True)
                Path.mkdir(dir_path, parents=True, exist_ok=True)
                trg_path = Path(fpath.replace("src", "converted"), exist_ok=True)
                shutil.copyfile(fpath, trg_path)
                print(fpath)
                print(trg_path)

# unzip_source(zipped_source, unzipped_source)
# convert_to_markdown(unzipped_source)
move_markdown(unzipped_source, markdown_path)