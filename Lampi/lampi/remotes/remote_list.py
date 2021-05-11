from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ListProperty
#from lampi.remotes.header import Header
from lampi.remotes.remote_cell import RemoteCell

class RemoteList(BoxLayout):

    saved_remotes = ListProperty([])
    blacklisted_remotes = ListProperty([])

    def __init__(self, *args, **kwargs):
        super(BoxLayout, self).__init__(*args, **kwargs)

    def on_saved_remotes(self, instance, value):
        self._update_ui()

    def on_blacklisted_remotes(self, instance, value):
        self._update_ui()

    def _update_ui(self):
        print("Updating UI")
        print("  Saved remotes: {}".format(self.saved_remotes))
        print("  Banned remotes: {}".format(self.blacklisted_remotes))

        print(self.size)

        # Clear
        self.clear_widgets()

        # Update one-by-one
        for address in self.saved_remotes:
            cell = RemoteCell()
            cell.address = address
            cell.size = (300, 300)
            self.add_widget(cell)
#            self.add_widget(Label(text=address))
#            self.add_widget(Button(text='Block'))

        for address in self.blacklisted_remotes:
            self.add_widget(Label(text=address))
            self.add_widget(Button(text='Unblock'))

        self._trigger_layout()
