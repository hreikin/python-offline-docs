from pathlib import Path
import zipfile, os, shutil
import pypandoc
from bs4 import BeautifulSoup


zipped_source = "/home/hreikin/git/python-offline-docs/file_download/output/downloads/full"
unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/src/"
markdown_path = "/home/hreikin/git/python-offline-docs/file_process/output/converted/"
test_unzipped_source = "/home/hreikin/git/python-offline-docs/file_process/output/test-src/"
test_markdown_path = "/home/hreikin/git/python-offline-docs/file_process/output/test-converted/"

def unzip_source(source_path, output_path):
    """Unzips all source files into the output path."""
    os.chdir(source_path)
    for file in os.listdir(source_path):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as item:
                item.extractall(output_path)

def prepare_soup(source_path):
    """Walks through the source path and finds all HTML files, creates a merged 
    file name for each one found before calling create_soup() to open/create the 
    files."""
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            if filename.endswith('.html'):
                source_file = os.path.join(root, filename)
                output_file = root + "/" + filename.replace(".html", "-MERGED-FILE.html")
                create_soup(source_file, output_file)


def create_soup(source_file, output_file):
    """Opens the source_file and targets HTML elements to create separate 
    variables for each item which are used to create the final merged file."""
    print(f'Opening HTML File: {source_file}')
    with open(source_file) as handle:
        soup = BeautifulSoup(handle, "html.parser")
    head_soup = soup.find("head")
    body_soup = soup.find("body")
    footer_soup = soup.find("footer")

    # Changes all internal link file extensions from html to rst.
    # for a in body_html.find_all("a", class_="reference internal"):
    #     a['href'] = a['href'].replace(".html", ".rst")

    # Creates a file from a soup object.
    # print(f'Creating Merged HTML File: {output_file}')
    # output = pypandoc.convert_text(body_html, "html", format="html", outputfile=output_file)
    # assert output == ""



def copy_final_file(source_path, output_path):
    """Copies all files that end with '.html' from one location to another. 
    Needs improving."""
    src = Path(source_path, exist_ok=True)
    trg = Path(output_path, exist_ok=True)
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