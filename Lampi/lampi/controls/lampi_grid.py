import json
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.BoxLayout import BoxLayout
from kivy.properties import NumericProperty


PRESET_FOLDER_DIRECTORY = '../presets/'
PRESETS = [
    PRESET_FOLDER_DIRECTORY + "preset" + str(1),
    PRESET_FOLDER_DIRECTORY + "preset" + str(2),
    PRESET_FOLDER_DIRECTORY + "preset" + str(3),
]

class PresetRow(BoxLayout):
    pass

class LampiGrid(Widget):

    preset_num = NumericProperty(0)

    def __init__(self, **kwargs):
        super(GridLayout, self).__init__(**kwargs)

    def _get_preset(self, index):
        with open(PRESETS[index] + ".json") as f:
            preset = json.load(f)

        return preset

    def _populate_grid(self, instance, value):
        preset_json = self._get_preset(self.preset_num)
        for state in preset_json['stateList']:
            self.root.ids.container.add_widget(PresetRow(text='works'))