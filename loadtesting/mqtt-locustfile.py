import json
import random
import resource

from locust import TaskSet, task

from mqtt_locust import MQTTLocust

resource.setrlimit(resource.RLIMIT_NOFILE, (999999, 999999))

TIMEOUT = 0.5      # put pretty tight time constraints on message ACK
REPEAT_COUNT = 10  # we will assume we get a burst of messages whenever user
#                    interacts with touchscreen

# topics and QoS
# 'lamp/set_config' 1
# 'lamp/changed' 1
#     lots of messages when user drags slider, not many for on/off
#
# 'lamp/connection/+/state' 1
#    not very many messages
#    topics:
#      'lamp/connection/lamp_service/state'
#      'lamp/connection/lamp_ui/state'
#      'lamp/connection/lamp_bt_peripheral/state'
#    '0' or '1'
#
# 'lamp/bluetooth' 1
#     only generates messages when bluetooth device connected
#     when connected, generates a message every second
#     { 'client': client_address, 'rssi': <integer>}

# for loadtesting purposes, we can ignore messages to the
#   'lamp/connection/+/state' and 'lamp/bluetooth' topics
#   - their frequency is so low as to be neglible

MAX_DEVICE = 10000
DEVICE_ID_BASE = 0x1e0000000000


class MyTaskSet(TaskSet):

    def on_start(self):
        self.device_id = DEVICE_ID_BASE + random.randint(0, MAX_DEVICE-1)

    def _generate_bridged_topic(self, device_topic):
        return 'devices/{}{}'.format(self.device_id, device_topic)

    @task(1)
    def lamp_changed(self):
        # from the bridge perspective, publishing lamp changed notifications
        # from the LAMPI to the EC2 infrastructure probably worst case load
        self.client.publish(
                self._generate_bridged_topic('lamp/changed'),
                self.payload(),
                qos=1,
                timeout=TIMEOUT,
                repeat=REPEAT_COUNT,
                name='lamp/changed'
                )

    def payload(self):
        payload = {
            'on': random.choice(['true', 'false']),
            'color': {
                'h': random.random(),
                's': random.random(),
            },
            'brightness': random.random(),
            'client': 'locust',
        }
        return json.dumps(payload)


class MyLocust(MQTTLocust):
    task_set = MyTaskSet
    # we assume, worst-case, that a user drags a slider, and then
    #   waits 1-2 seconds before doing another operation
    min_wait = 1000
    max_wait = 2000
