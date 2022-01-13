import simple_menu
from file_download.spiders.get_files import run_spider

app_name = "File Download"
options = {
    'view': {
        'title':"Run Spider To Generate Links",
        'func': run_spider
    },
    'exit': {
        'title':"Exit the program.",
        'func': simple_menu.close_statement
    },

}

simple_menu.main_menu(options, app_name)