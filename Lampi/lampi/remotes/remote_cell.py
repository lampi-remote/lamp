from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty, BooleanProperty

class RemoteCell(BoxLayout):

    bg_color = ListProperty([1, 0, 1])
    address = StringProperty("addr")
    connected = BooleanProperty(False)
    banned = BooleanProperty(False)
    button_text = StringProperty("Button")
    detail_text = StringProperty("Detail")

    def __init__(self, *args, **kwargs):
        super(BoxLayout, self).__init__(*args, **kwargs)
        print("Initialized")

    def on_address(self, instance, value):
        print("adr")
        print(value)

    def on_banned(self, instance, value):
        self._update_detail_text()
        self.button_text = "Unblock" if value else "Block"

    def on_connected(self, instance, value):
        self._update_detail_text()

    def _update_detail_text(self):
        if self.banned:
            self.detail_text = "Blocked"
        elif self.connected:
            self.detail_text = "Connected"
        else:
            self.detail_text = "Not connected"
