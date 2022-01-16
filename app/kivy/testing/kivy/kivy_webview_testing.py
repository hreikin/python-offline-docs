from kivy.app import App
from kivy.metrics import dp
from kivy.uix.behaviors import TouchRippleBehavior
from kivy.uix.button import Button
from kivy.lang import Builder
import webview

KV = """
Screen:
    canvas:
        Color:
            rgba: 0.9764705882352941, 0.9764705882352941, 0.9764705882352941, 1
        Rectangle:
            pos: self.pos
            size: self.size
"""

class MainApp(App):
    def build(self):
        screen = webview.create_window('Python Offline Docs', '../../file_process/output/src-backup/python-3.10.1-docs-html/index.html')
        webview.start(http_server=True)
        return screen


MainApp().run()