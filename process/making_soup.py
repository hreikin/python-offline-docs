from pathlib import Path
import zipfile, os, shutil
import pypandoc
from bs4 import BeautifulSoup


zipped_source = "/home/hreikin/git/python-offline-docs/download/output/downloads/full"
unzipped_source = "/home/hreikin/git/python-offline-docs/process/output/src/"
markdown_path = "/home/hreikin/git/python-offline-docs/process/output/converted/"
test_unzipped_source = "/home/hreikin/git/python-offline-docs/process/output/test-src/"
test_output_path = "/home/hreikin/git/python-offline-docs/process/output/test-output/"

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
                # output_file = root + "/" + filename.replace(".html", "-MERGED-FILE.html")
                create_soup(source_file)


def create_soup(source_file):
    """Opens the source_file and targets HTML elements to create separate 
    variables for each item which are used to create the final merged file."""
    print(f'Opening HTML File: {source_file}')
    with open(source_file) as handle:
        soup = BeautifulSoup(handle, "html.parser")
    
    # Variables to be used for constructing page partials.
    head_soup = soup.find("head")
    head_title_soup = head_soup.title
    head_script_soup = head_soup.find_all("script")
    head_link_soup = head_soup.find_all("link")
    head_style_soup = head_soup.find_all("style")
    body_soup = soup.find("div", class_="body", role="main")
    sidebar_soup = soup.find("div", class_="sphinxsidebarwrapper")
    sidebar_link_soup = sidebar_soup.find_all("a", href=True)
    sidebar_link_pairs = []
    sidebar_bottom = ['</nav>\n', '</div>\n', '<main class="mdl-layout__content mdl-color--grey-100">\n', '<div class="mdl-grid demo-content">\n']
    finished_body_soup = []
    finished_head_soup = []
    partial_pages = [
        ("-HEAD-PARTIAL.html", finished_head_soup),  
        ("-BODY-PARTIAL.html", finished_body_soup),
        ]

    # Create a tuple of the href and link text found in the sidebar and then 
    # append it to a list.
    for item in sidebar_link_soup:
        item_tuple = (item['href'], item.contents[0])
        sidebar_link_pairs.append(item_tuple)

    # Construct the body partial file. This gets inserted with the pandoc 
    # "--include-before-body" option.
    for href, text in sidebar_link_pairs:
        finished_body_soup.append(f'<a class="mdl-navigation__link" href="{href}">{text}</a>\n')
    for item in sidebar_bottom:
        finished_body_soup.append(item)
    finished_body_soup.append(str(body_soup))

    # Construct the head partial file. This gets inserted with the pandoc 
    # "--include-in-header" option.
    finished_head_soup.append(str(head_title_soup) + "\n")
    for item in head_script_soup:
        finished_head_soup.append(str(item) + "\n")
    for item in head_link_soup:
        finished_head_soup.append(str(item) + "\n")
    for item in head_style_soup:
        finished_head_soup.append(str(item) + "\n")

    # Creates the partials from the finished soup.
    for file_extension, soup in partial_pages:
        # Constructs partial output file names.
        output_file = str(source_file).replace(".html", f"{file_extension}")
        print(f'Creating Merged HTML File: {output_file}')
        with open(output_file, "w") as stream:
            for item in soup:
                stream.write(item)

    # Use pypandoc to insert the partials into a template file.
    head_partial = str(source_file).replace(".html", "-HEAD-PARTIAL.html")
    body_partial = str(source_file).replace(".html", "-BODY-PARTIAL.html")
    template_file = "/home/hreikin/git/python-offline-docs/process/templates/index.html"
    finished_file = str(source_file).replace(".html", "-FINAL.html")
    pandoc_args = [
        "-s",
        f"--include-in-header={head_partial}",
        f"--include-before-body={body_partial}",
        f"--template={template_file}",
    ]
    pypandoc.convert_text("", "html", format="html", extra_args=pandoc_args, outputfile=finished_file)

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

prepare_soup(test_unzipped_source)