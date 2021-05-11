import platform
import kivy
from kivy.app import App
kivy.require('1.9.0')
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty, ListProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.stacklayout import StackLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from kivy.uix.button import Button
from math import fabs
import json
import os
from paho.mqtt.client import Client
import pigpio
from lamp_common import *
import lampi.lampi_util
import remotes
from mixpanel import Mixpanel
from mixpanel_async import AsyncBufferedConsumer


class ScrollButton(Button):
    pass

NEW_REMOTE_TOPIC = "lamp/bluetooth/remote"
DISCOVERY_TOPIC = "lamp/bluetooth/discovery"
DISCONNECT_TOPIC = "lamp/bluetooth/disconnect"

MQTT_CLIENT_ID = "lamp_ui"

PRESET_FOLDER_DIRECTORY = './presets/'
PRESETS = [
    PRESET_FOLDER_DIRECTORY + "preset" + str(1),
    PRESET_FOLDER_DIRECTORY + "preset" + str(2),
    PRESET_FOLDER_DIRECTORY + "preset" + str(3),
]

try:
    from .mixpanel_settings import MIXPANEL_TOKEN
except (ModuleNotFoundError, ImportError) as e:
    MIXPANEL_TOKEN = "UPDATE TOKEN IN mixpanel_settings.py"

version_path = os.path.join(os.path.dirname(__file__), '__VERSION__')
try:
    with open(version_path, 'r') as version_file:
        LAMPI_APP_VERSION = version_file.read()
except IOError:
    # if version file cannot be opened, we'll stick with unknown
    LAMPI_APP_VERSION = 'Unknown'


class LampiApp(App):
    _updated = False
    _updatingUI = False
    _hue = NumericProperty()
    _saturation = NumericProperty()
    _brightness = NumericProperty()
    _preset = NumericProperty()
    lamp_is_on = BooleanProperty()
    _preset_color = NumericProperty()
    _preset_temp = NumericProperty()

    remote_connection = StringProperty("[b]Connected:[/b] No")
    trusted_remotes = StringProperty("[b]Trusted Remotes:[/b] None")

    mp = Mixpanel(MIXPANEL_TOKEN, consumer=AsyncBufferedConsumer())

    def _get_hue(self):
        return self._hue

    def _set_hue(self, value):
        self._hue = value

    def _get_saturation(self):
        return self._saturation

    def _set_saturation(self, value):
        self._saturation = value

    def _get_brightness(self):
        return self._brightness

    def _set_brightness(self, value):
        self._brightness = value

    def _get_preset(self):
        return self._preset

    def _set_preset(self, value):
        self._preset = value

    def _get_preset_color(self):
        return self._preset_color

    def _set_preset_color(self, value):
        self._preset_color = value

    def _get_preset_temp(self):
        return self._preset_temp

    def _set_preset_temp(self, value):
        self._preset_temp = value

    hue = AliasProperty(_get_hue, _set_hue, bind=['_hue'])
    saturation = AliasProperty(_get_saturation, _set_saturation,
                               bind=['_saturation'])
    brightness = AliasProperty(_get_brightness, _set_brightness,
                               bind=['_brightness'])
    preset = AliasProperty(_get_preset, _set_preset,
                               bind=['_preset'])
    preset_color = AliasProperty(_get_preset_color, _set_preset_color,
                               bind=['_preset_color'])
    preset_temp = AliasProperty(_get_preset_temp, _set_preset_temp,
                               bind=['_preset_temp'])
    gpio17_pressed = BooleanProperty(False)
    device_associated = BooleanProperty(True)

    def on_start(self):
        self._publish_clock = None
        self.mqtt_broker_bridged = False
        self._associated = True
        self.association_code = None
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.enable_logger()
        self.mqtt.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
                           qos=2, retain=True)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self.set_up_GPIO_and_device_status_popup()
        self.associated_status_popup = self._build_associated_status_popup()
        self.associated_status_popup.bind(on_open=self.update_popup_associated)

        self._remote = None
        self._popup_remote = None
        self.pairing_popup = self._build_pairing_popup()

        self._update_remotes_ui()

        self.discoverswitch = self.root.ids.discoverswitch
        self.discoverswitch.bind(active=self.toggle_discovery)

        Clock.schedule_interval(self._poll_associated, 0.1)

    def _build_associated_status_popup(self):
        return Popup(title='Associate your Lamp',
                     content=Label(text='Msg here', font_size='30sp'),
                     size_hint=(1, 1), auto_dismiss=False)

    def _build_pairing_popup(self):
        layout = StackLayout()
        label = Label(text='A new remote is attempting\nto connect to your lamp.\n\nWould you like to\nallow it?', size_hint=(1, None), padding=(4, 4))
        label.bind(size=self._update_textsize)
        deny = Button(text='Deny', size_hint=(0.49, None), height=40)
        allow = Button(text='Trust', size_hint=(0.49, None), height=40)
        allow.on_release = self._allow_remote
        deny.on_release = self._decline_remote
        layout.add_widget(label)
        layout.add_widget(Label(size_hint=(1, None), height=15))
        layout.add_widget(deny)
        layout.add_widget(Label(size_hint=(0.02, None), height=1))
        layout.add_widget(allow)
        return Popup(title='Remote Pairing Request',
                     content=layout,
                     size_hint=(1, 0.68), auto_dismiss=False)

    def _update_textsize(self, instance, value):
        instance.text_size = (value[0], value[1])

    def on_new_remote(self, client, userdata, message):
        isEmpty = message.payload == b''

        if isEmpty:
            self._remote = None
        else:
            remote = json.loads(message.payload.decode('utf-8'))
            self._remote = remote
            self._popup_remote = remote
            if (not remote['allowed']):
                self.pairing_popup.open()

        self._update_remotes_ui()


    def _allow_remote(self):
        print("Pairing allowed for {}".format(self._popup_remote['address']))
        remotes.saveAddress(self._popup_remote['address'])
        self._remote = None
        self._popup_remote = None
        self.pairing_popup.dismiss()
        self._update_remotes_ui()

        # Display confirmation
        conf = Popup(title='Remote Trusted',
                     content=Label(text='You have successfully trusted\nyour remote. Pair it again to\nuse it'),
                     size_hint=(1, 0.5), auto_dismiss=False)

        conf.open()
        Clock.schedule_once(lambda dt: conf.dismiss(), 3)

    def _decline_remote(self):
        print("Pairing denied for {}".format(self._popup_remote['address']))
        self._popup_remote = None
        self._remote = None
        self.pairing_popup.dismiss()
        self._update_remotes_ui()

    def clear_remotes(self):
        remotes.clear()
        self.mqtt.publish(DISCONNECT_TOPIC, b'')
        self._update_remotes_ui()

    def toggle_discovery(self, instance, value):
        # Send message accordingly
        self.mqtt.publish(DISCOVERY_TOPIC, ("true" if value else "false").encode('utf8'), retain=True)

    def _update_remotes_ui(self):
        savedremotes = remotes._read()
        statustext = "[b]Connected:[/b] False\n\n"

        if (self._remote is not None):
            self.remote_connection = "[b]Connected:[/b] [color=32ff32]{}[/color]".format(self._remote['address'])
        else:
            self.remote_connection = "[b]Connected:[/b] [color=ff3232]Not connected[/color]"

        if (len(savedremotes) == 0):
            self.trusted_remotes = "[b]Trusted Remotes:[/b] None"
        else:
            self.trusted_remotes = "[b]Trusted Remotes:[/b]\n" + "\n".join([" • {}".format(addr) for addr in savedremotes])

    def on_hue(self, instance, value):
        if self._updatingUI:
            return
        self._track_ui_event('Slider Change',
                             {'slider': 'hue-slider', 'value': value})
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_saturation(self, instance, value):
        if self._updatingUI:
            return
        self._track_ui_event('Slider Change',
                             {'slider': 'saturation-slider', 'value': value})
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_brightness(self, instance, value):
        if self._updatingUI:
            return
        self._track_ui_event('Slider Change',
                             {'slider': 'brightness-slider', 'value': value})
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_lamp_is_on(self, instance, value):
        if self._updatingUI:
            return
        self._track_ui_event('Toggle Power', {'isOn': value})
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_preset_temp(self, instance, value):
        if self._updatingUI:
            return
        self._track_ui_event('Slider Change',
                             {'slider': 'preset_hue_slider', 'value': value})

    def _track_ui_event(self, event_name, additional_props={}):
        device_id = lampi.lampi_util.get_device_id()

        event_props = {'event_type': 'ui', 'interface': 'lampi',
                       'device_id': device_id}
        event_props.update(additional_props)

        self.mp.track(device_id, event_name, event_props)

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt.publish(client_state_topic(MQTT_CLIENT_ID), b"1",
                          qos=2, retain=True)
        self.mqtt.message_callback_add(TOPIC_LAMP_CHANGE_NOTIFICATION,
                                       self.receive_new_lamp_state)
        self.mqtt.message_callback_add(broker_bridge_connection_topic(),
                                       self.receive_bridge_connection_status)
        self.mqtt.message_callback_add(TOPIC_LAMP_ASSOCIATED,
                                       self.receive_associated)
        self.mqtt.message_callback_add(NEW_REMOTE_TOPIC,
                                       self.on_new_remote)
        self.mqtt.subscribe(broker_bridge_connection_topic(), qos=1)
        self.mqtt.subscribe(TOPIC_LAMP_CHANGE_NOTIFICATION, qos=1)
        self.mqtt.subscribe(TOPIC_LAMP_ASSOCIATED, qos=2)
        self.mqtt.subscribe(NEW_REMOTE_TOPIC, qos=2)

    def _poll_associated(self, dt):
        # this polling loop allows us to synchronize changes from the
        #  MQTT callbacks (which happen in a different thread) to the
        #  Kivy UI
        self.device_associated = self._associated

    def receive_associated(self, client, userdata, message):
        # this is called in MQTT event loop thread
        new_associated = json.loads(message.payload.decode('utf-8'))
        if self._associated != new_associated['associated']:
            if not new_associated['associated']:
                self.association_code = new_associated['code']
            else:
                self.association_code = None
            self._associated = new_associated['associated']

    def on_device_associated(self, instance, value):
        if value:
            self.associated_status_popup.dismiss()
        else:
            self.associated_status_popup.open()

    def update_popup_associated(self, instance):
        code = self.association_code[0:6]
        instance.content.text = ("Please use the\n"
                                 "following code\n"
                                 "to associate\n"
                                 "your device\n"
                                 "on the Web\n{}".format(code)
                                 )

    def receive_bridge_connection_status(self, client, userdata, message):
        # monitor if the MQTT bridge to our cloud broker is up
        if message.payload == b"1":
            self.mqtt_broker_bridged = True
        else:
            self.mqtt_broker_bridged = False

    def receive_new_lamp_state(self, client, userdata, message):
        new_state = json.loads(message.payload.decode('utf-8'))
        Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)

    def _update_ui(self, new_state):
        if self._updated and new_state['client'] == MQTT_CLIENT_ID:
            # ignore updates generated by this client, except the first to
            #   make sure the UI is syncrhonized with the lamp_service
            return
        self._updatingUI = True
        try:
            if 'color' in new_state:
                self.hue = new_state['color']['h']
                self.saturation = new_state['color']['s']
            if 'brightness' in new_state:
                self.brightness = new_state['brightness']
            if 'on' in new_state:
                self.lamp_is_on = new_state['on']
        finally:
            self._updatingUI = False

        self._updated = True

    def _update_leds(self):
        msg = {'color': {'h': self._hue, 's': self._saturation},
               'brightness': self._brightness,
               'on': self.lamp_is_on,
               'client': MQTT_CLIENT_ID}
        self.mqtt.publish(TOPIC_SET_LAMP_CONFIG,
                          json.dumps(msg).encode('utf-8'),
                          qos=1)
        self._publish_clock = None

    def set_up_GPIO_and_device_status_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.network_status_popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_device_status_popup)

    def _build_network_status_popup(self):
        return Popup(title='Device Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_device_status_popup(self, instance):
        interface = "wlan0"
        ipaddr = lampi.lampi_util.get_ip_address(interface)
        deviceid = lampi.lampi_util.get_device_id()
        msg = ("Version: {}\n"
               "{}: {}\n"
               "DeviceID: {}\n"
               "Broker Bridged: {}\n"
               "Async Analytics"
               ).format(
                        LAMPI_APP_VERSION,
                        interface,
                        ipaddr,
                        deviceid,
                        self.mqtt_broker_bridged)
        instance.content.text = msg

    def on_gpio17_pressed(self, instance, value):
        if value:
            self.network_status_popup.open()
        else:
            self.network_status_popup.dismiss()

    def _poll_GPIO(self, dt):
        # GPIO17 is the rightmost button when looking front of LAMPI
        self.gpio17_pressed = not self.pi.read(17)

    def write_preset(self, num):

        filewrite = {
            "stateList": [
                {
                    "state": {
                        "h": self._preset_color,
                        "s": 1.0,
                        "b": 1.0
                    },
                    "smooth": False,
                    "waitTime": 0,
                    "transitionTime": 0
                },
            ],
            'loop': False
        }

        with open(PRESETS[num - 1] + ".json", "w") as f:
            json.dump(filewrite, f)
