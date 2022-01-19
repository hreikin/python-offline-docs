import zipfile, glob, os, shutil
import pypandoc
from bs4 import BeautifulSoup

def unzip_source(source_path, output_path):
    """Unzips all source files into the output path."""
    source_path = os.path.realpath(source_path)
    output_path = os.path.realpath(output_path)
    os.chdir(source_path)
    for file in os.listdir(source_path):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as item:
                item.extractall(output_path)

def copy_to_location(source_path, destination_path, override=False):
    """
    Recursive copies files from source  to destination directory.
    :param source_path: source directory
    :param destination_path: destination directory
    :param override if True all files will be overritten, otherwise if false skip file
    :return: count of copied files
    """
    source_path = os.path.realpath(source_path)
    destination_path = os.path.realpath(destination_path)
    files_count = 0
    if not os.path.exists(destination_path):
        os.mkdir(destination_path)
    items = glob.glob(source_path + '/*')
    for item in items:
        if os.path.isdir(item):
            path = os.path.join(destination_path, item.split('/')[-1])
            files_count += copy_to_location(source_path=item, destination_path=path, override=override)
        else:
            file = os.path.join(destination_path, item.split('/')[-1])
            if not os.path.exists(file) or override:
                shutil.copyfile(item, file)
                files_count += 1
    return files_count

def prepare_soup(source_path):
    """Walks through the source path and finds all HTML files, creates a merged 
    file name for each one found before calling create_soup() to open/create the 
    files."""
    source_path = os.path.realpath(source_path)
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            if filename.endswith('.html'):
                original_file = os.path.join(root, filename)
                copied_file = root + "/" + filename.replace(".html", "-ORIGINAL.html")
                shutil.move(original_file, copied_file)
                create_soup(copied_file)

def create_soup(source_file):
    """Opens the source_file and targets HTML elements to create separate 
    variables for each item which are used to create the final merged file."""
    source_file = os.path.realpath(source_file)
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
        output_file = str(source_file).replace("-ORIGINAL.html", f"{file_extension}")
        print(f'Creating Merged HTML File: {output_file}')
        with open(output_file, "w") as stream:
            for item in soup:
                stream.write(item)

    # Use pypandoc to insert the partials into a template file.
    head_partial = str(source_file).replace("-ORIGINAL.html", "-HEAD-PARTIAL.html")
    body_partial = str(source_file).replace("-ORIGINAL.html", "-BODY-PARTIAL.html")
    finished_file = str(source_file).replace("-ORIGINAL.html", ".html")
    template_file = os.path.realpath("templates/index.html")
    template_css = os.path.relpath("../app/pod/styles.css", start=finished_file).lstrip("..").lstrip("/") # os.path.realpath("templates/styles.css")
    pandoc_args = [
        "-s",
        f"--css={template_css}",
        f"--include-in-header={head_partial}",
        f"--include-before-body={body_partial}",
        f"--template={template_file}",
    ]
    pypandoc.convert_text("", "html", format="html", extra_args=pandoc_args, outputfile=finished_file)

def clean_up(source_path):
    source_path = os.path.realpath(source_path)
    remove = ["-PARTIAL.html", "-ORIGINAL.html"]
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            for item in remove:
                if filename.endswith(item):
                    print(f"Removing: {root}/{filename}")
                    os.remove(f"{root}/{filename}")

def move_to_location(source_path, output_path):
    for file in os.listdir(source_path):
        shutil.move(source_path + file, output_path + file)



# zip_paths = "../download/output/downloads/full/"
# zip_output = "output/src/"
# unzip_source(zip_paths, zip_output)

source_path = "output/test-src/"
output_path = "../app/pod/"
print("Copying Source.")
copy_to_location(source_path, output_path)

print("Preparing Soup.")
prepare_soup(output_path)

template_source_path = "templates/"
template_output_path = "../app/pod/"
print("Copying Template.")
copy_to_location(template_source_path, template_output_path)

print("Cleaning Up.")
clean_up(output_path)

# final_path = "../app/pod/"
# print("Moving To Final Location.")
# move_to_location(output_path, final_path)