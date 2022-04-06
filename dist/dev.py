import webview

class App:
  def __init__(self):
      return

app = App()

window = webview.create_window("Python Offline Docs", "../pod/python-3.10.1-docs-html/about.html", js_api=App())
webview.start(http_server=True)