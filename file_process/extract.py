from pathlib import Path
import zipfile, os, shutil
import pypandoc
from bs4 import BeautifulSoup
import re

zipped_source = "/home/hreikin/git/python-offline-docs/file_download/output/downloads/full"
unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/src/"
markdown_path = "/home/hreikin/git/python-offline-docs/file_process/output/converted/"
test_unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/test-src/"
test_markdown_path = "/home/hreikin/git/python-offline-docs/file_process/output/test-converted/"

def unzip_source(source_path, output_path):
    os.chdir(source_path)
    for file in os.listdir(source_path):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as item:
                item.extractall(output_path)

def convert_to_rst(unzipped_source):
    for root, dirnames, filenames in os.walk(unzipped_source):
        for filename in filenames:
            if filename.endswith('.html'):
                fname = os.path.join(root, filename)
                rstname = root + "/" + filename.replace(".html", ".rst")
                create_soup(fname, rstname)

def copy_rst(source_path, target_path):
    src = Path(source_path, exist_ok=True)
    trg = Path(target_path, exist_ok=True)
    for root, dirnames, filenames in os.walk(src):
        for filename in filenames:
            if filename.endswith('.rst'):
                fpath = os.path.join(root, filename)
                dir_path = Path(fpath.replace("src", "converted").rstrip(filename), exist_ok=True)
                Path.mkdir(dir_path, parents=True, exist_ok=True)
                trg_path = Path(fpath.replace("src", "converted"), exist_ok=True)
                shutil.copyfile(fpath, trg_path)
                print(fpath)
                print(trg_path)

def create_soup(fname, rstname):
    print(f'Opening HTML File: {fname}')
    with open(fname) as handle:
        soup = BeautifulSoup(handle, "html.parser")

    body_html = soup.find("div", class_="body", role="main")
    tags = body_html.find_all("a", class_="reference internal")
    log_file = "./error.log"
    try:
        for item in tags:
            old_item = str(item)
            new_item = re.sub(".html", ".rst", str(item))
            body_html = re.sub(old_item, new_item, str(body_html))
    except:
        message = "EXCEPTION: Tag Loop"
        with open(log_file, "a") as handle:
            handle.write(message + "\n" + fname + "\n")
    try:
        print(f'Creating reStructuredText File: {rstname}')
        output = pypandoc.convert_text(body_html, "rst", format="html", outputfile=rstname)
        assert output == ""
    except:
        message = "EXCEPTION: Convert with pypandoc"
        with open(log_file, "a") as handle:
            handle.write(message + "\n" + fname + "\n")

# unzip_source(zipped_source, unzipped_source)
convert_to_rst(test_unzipped_source)
copy_rst(test_unzipped_source, test_markdown_path)
# rstname = "/home/hreikin/git/python-offline-docs/file_process/output/single-converted/python-3.10.1-docs-html/about.rst"
# fname="/home/hreikin/git/python-offline-docs/file_process/output/single-src/python-3.10.1-docs-html/about.html"
# create_soup(fname, rstname)