import webview

webview.create_window('Python Offline Docs', '../../file_process/output/src-backup/python-3.10.1-docs-html/index.html')
webview.start(http_server=True)