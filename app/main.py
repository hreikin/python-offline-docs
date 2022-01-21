import webview

webview.create_window('Python Offline Docs', '../pod/python-3.10.1-docs-html/index.html')
webview.start(http_server=True)