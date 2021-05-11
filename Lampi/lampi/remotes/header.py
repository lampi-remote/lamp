from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.graphics import Rectangle, Color

class Header(Label):

    def __init__(self, *args, **kwargs):
        Label.__init__(self, *args, **kwargs)
