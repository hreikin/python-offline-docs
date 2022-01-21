import zipfile, glob, os, shutil
import pypandoc
from bs4 import BeautifulSoup

def unzip_source(source_path, output_path):
    """
    Unzips all source_path zip files into the output path.
    
    :param source_path: Path to the folder containing zip files.
    :param output_path: Path to unzip the files and folders into.
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
    
    :param source_path: source directory
    :param destination_path: destination directory
    :param override: if True all files will be overwritten, otherwise if false skip file.
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
    """
    Walks through the source path to find and rename all HTML files 
    before calling create_soup() on the individual files to create the 
    HTML partials and convert with pandoc.
    
    :param source_path: Root directory to start searching for HTML files.
    """
    source_path = os.path.realpath(source_path)
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            if filename.endswith('.html'):
                original_file = os.path.join(root, filename)
                copied_file = root + "/" + filename.replace(".html", "-ORIGINAL.html")
                shutil.move(original_file, copied_file)
                create_soup(copied_file)

def create_soup(source_file):
    """
    Opens the source_file and targets HTML elements to create separate 
    variables for constructing the HTML partials. Once the partials are 
    created they are used with pypandoc templates to create a final file.
    
    :param source_file: The file to create partials from.
    :return finished_file: The final converted file.
    """
    source_file = os.path.realpath(source_file)
    print(f'Opening Source HTML File: {source_file}')
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
        print(f'Creating Partial HTML File: {output_file}')
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
    print(f"Creating Final HTML File With Pandoc: {finished_file}")
    pypandoc.convert_text("", "html", format="html", extra_args=pandoc_args, outputfile=finished_file)

def clean_up(source_path):
	"""
	Walks through the source path and removes the partial and original 
	files after conversion.
	
	:param source_path: The location of the files to search through.
	"""
    source_path = os.path.realpath(source_path)
    remove = ["-PARTIAL.html", "-ORIGINAL.html"]
    for root, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            for item in remove:
                if filename.endswith(item):
                    print(f"Removing: {root}/{filename}")
                    os.remove(f"{root}/{filename}")

def move_to_location(source_path, output_path):
	"""
	Moves all files and folders from one location to another.
	
	:param source_path: Location of the files and folders to be moved.
	:param output_path: Location to be moved to.
	"""
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




# All hrefs need "../images" replacing with a variable so it can be set each 
# time a partial is created.

# Include the below before "</head>" tag using "$for(header-includes)$" pandoc 
# variable to insert.

# <!-- Add to homescreen for Chrome on Android -->
# <meta name="mobile-web-app-capable" content="yes">
# <link rel="icon" sizes="192x192" href="../images/android-desktop.png">

# <!-- Add to homescreen for Safari on iOS -->
# <meta name="apple-mobile-web-app-capable" content="yes">
# <meta name="apple-mobile-web-app-status-bar-style" content="black">
# <meta name="apple-mobile-web-app-title" content="Material Design Lite">
# <link rel="apple-touch-icon-precomposed" href="../images/ios-desktop.png">

# <!-- Tile icon for Win8 (144x144 + tile color) -->
# <meta name="msapplication-TileImage" content="../images/touch/ms-touch-icon-144x144-precomposed.png">
# <meta name="msapplication-TileColor" content="#3372DF">

# <link rel="shortcut icon" href="../images/favicon.png">

# Include the below after "<body>" tag using "$for(include-before)$" pandoc 
# variable to insert.

# <div class="demo-layout mdl-layout mdl-js-layout mdl-layout--fixed-drawer mdl-layout--fixed-header">
#   <header class="demo-header mdl-layout__header mdl-color--grey-100 mdl-color-text--grey-600">
#     <div class="mdl-layout__header-row">
#       <span class="mdl-layout-title">Home</span>
#       <div class="mdl-layout-spacer"></div>
#       <div class="mdl-textfield mdl-js-textfield mdl-textfield--expandable">
#         <label class="mdl-button mdl-js-button mdl-button--icon" for="search">
#           <i class="material-icons">search</i>
#         </label>
#         <div class="mdl-textfield__expandable-holder">
#           <input class="mdl-textfield__input" type="text" id="search">
#           <label class="mdl-textfield__label" for="search">Enter your query...</label>
#         </div>
#       </div>
#       <button class="mdl-button mdl-js-button mdl-js-ripple-effect mdl-button--icon" id="hdrbtn">
#         <i class="material-icons">more_vert</i>
#       </button>
#       <ul class="mdl-menu mdl-js-menu mdl-js-ripple-effect mdl-menu--bottom-right" for="hdrbtn">
#         <li class="mdl-menu__item">About</li>
#         <li class="mdl-menu__item">Contact</li>
#         <li class="mdl-menu__item">Legal information</li>
#       </ul>
#     </div>
#   </header>
#   <div class="demo-drawer mdl-layout__drawer mdl-color--blue-grey-900 mdl-color-text--blue-grey-50">
#     <header class="demo-drawer-header">
#       <img src="../images/python-logo.png" class="demo-avatar">
#       <!-- <div class="demo-avatar-dropdown">
#         <span>hello@example.com</span>
#         <div class="mdl-layout-spacer"></div>
#         <button id="accbtn" class="mdl-button mdl-js-button mdl-js-ripple-effect mdl-button--icon">
#           <i class="material-icons" role="presentation">arrow_drop_down</i>
#           <span class="visuallyhidden">Accounts</span>
#         </button>
#         <ul class="mdl-menu mdl-menu--bottom-right mdl-js-menu mdl-js-ripple-effect" for="accbtn">
#           <li class="mdl-menu__item">hello@example.com</li>
#           <li class="mdl-menu__item">info@example.com</li>
#           <li class="mdl-menu__item"><i class="material-icons">add</i>Add another account...</li>
#         </ul>
#       </div> -->
#     </header>
#     <nav class="demo-navigation mdl-navigation mdl-color--blue-grey-800">
