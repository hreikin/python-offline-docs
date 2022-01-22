import zipfile, glob, os, shutil, logging
import pypandoc
from bs4 import BeautifulSoup

###################################### LOGS #####################################
# Initialize the logger and specify the level of logging. This will log "DEBUG" 
# and higher messages to file and log "INFO" and higher messages to the console.
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S',
                    filename='making-soup-debug.log',
                    filemode='w')

# Define a "handler" which writes "DEBUG" messages or higher to the "sys.stderr".
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# Set a format which is simpler for console messages.
formatter = logging.Formatter('%(levelname)s: %(message)s')

# Tell the console "handler" to use this format.
console.setFormatter(formatter)

# Add the "handler" to the "root logger".
logging.getLogger('').addHandler(console)

def unzip_source(source_path, output_path):
    """
    Un-zips all source path zip files into the output path.
    
    :param source_path(str): Path to the folder containing zip files.
    :param output_path(str): Path to un-zip the files and folders into.
    """
    source_path = os.path.realpath(source_path)
    output_path = os.path.realpath(output_path)
    os.chdir(source_path)
    for file in os.listdir(source_path):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as item:
                item.extractall(output_path)

def copy_to_location(source_path, destination_path, override=False):
    """
    Recursively copies files from source to destination directory.
    
    :param source_path(str): Source directory that contains files and folders to be copied.
    :param destination_path(str): Destination directory to copy to.
    :param override(bool): If True all files will be overwritten, otherwise if false skip file.
    :return files_count(int): Count of copied files.
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
    """
    Walks through the source path to find and rename all HTML files 
    before calling create_soup() on the individual files to create the 
    HTML partials and convert with pandoc.
    
    :param source_path(str): Root directory to start searching for HTML files.
    """
    source_path = os.path.realpath(source_path)
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            if filename.endswith('.html'):
                original_file = os.path.join(root, filename)
                copied_file = root + "/" + filename.replace(".html", "-ORIGINAL.html")
                logging.info(f"Renamed '{original _file}' to '{copied_file}'.")
                shutil.move(original_file, copied_file)
                create_soup(copied_file)

def create_soup(source_file):
    """
    Opens the source_file and targets HTML elements to create separate 
    variables for constructing the HTML partials. Once the partials are 
    created they are used with pypandoc templates to create a final file.
    
    :param source_file(str): The file to create partials from.
    :return finished_file(str): The final converted file.
    """
    source_file = os.path.realpath(source_file)
    logging.info(f'Opening Source HTML File: {source_file}')
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
        logging.info(f'Creating Partial HTML File: {output_file}')
        with open(output_file, "w") as stream:
            for item in soup:
                stream.write(item)

    # Use pypandoc to insert the partials into a template file.
    head_partial = str(source_file).replace("-ORIGINAL.html", "-HEAD-PARTIAL.html")
    body_partial = str(source_file).replace("-ORIGINAL.html", "-BODY-PARTIAL.html")
    finished_file = str(source_file).replace("-ORIGINAL.html", ".html")
    pandoc_html_template = os.path.realpath("templates/index.html")
    pandoc_css_rel_link = os.path.relpath("../app/pod/styles.css", start=finished_file).lstrip("..").lstrip("/") # os.path.realpath("templates/styles.css")
    pandoc_images_rel_link = os.path.relpath("../app/pod/images/", start=finished_file).lstrip("..").lstrip("/")
    pandoc_args = [
        "-s",
        f"--css={pandoc_css_rel_link}",
        f"--variable=rel-images:{pandoc_images_rel_link}",
        f"--include-in-header={head_partial}",
        f"--include-before-body={body_partial}",
        f"--template={pandoc_html_template}",
    ]
    logging.info(f"Creating Final HTML File With Pandoc: {finished_file}")
    pypandoc.convert_text("", "html", format="html", extra_args=pandoc_args, outputfile=finished_file)

def clean_up(source_path):
    """
    Walks through the source path and removes the partial and original 
    files after conversion.
    
    :param source_path(str): The location of the files to search through.
    """
    source_path = os.path.realpath(source_path)
    remove = ["-PARTIAL.html", "-ORIGINAL.html"]
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            for item in remove:
                if filename.endswith(item):
                    logging.info(f"Removing: {root}/{filename}")
                    os.remove(f"{root}/{filename}")

def move_to_location(source_path, output_path):
    """
    Moves all files and folders from one location to another.
    
    :param source_path(str): Location of the files and folders to be moved.
    :param output_path(str): Location to be moved to.
    """
    for file in os.listdir(source_path):
        shutil.move(source_path + file, output_path + file)



# zip_paths = "../download/output/downloads/full/"
# zip_output = "output/src/"
# unzip_source(zip_paths, zip_output)

source_path = "output/src/"
output_path = "../app/"
print("Copying Source.")
copy_to_location(source_path, output_path)

print("Preparing Soup.")
prepare_soup(output_path)

template_source_path = "templates/"
template_output_path = "../app/"
print("Copying Template.")
copy_to_location(template_source_path, template_output_path)

print("Cleaning Up.")
clean_up(output_path)
