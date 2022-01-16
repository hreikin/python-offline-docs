from kivy.base import runTouchApp
from kivy.uix.rst import RstDocument
doc = RstDocument(source = '../../file_process/output/test-converted/python-3.10.1-docs-html/index.rst')
runTouchApp(doc)