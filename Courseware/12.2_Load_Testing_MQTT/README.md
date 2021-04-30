# MQTT Locust

Locust can be [extended](http://docs.locust.io/en/latest/testing-other-systems.html) to test non-HTTP systems.  Previous students in this course ([Andrew Mason](https://github.com/ajm188) and [Matthew Bentley](https://github.com/matthewbentley)) developed this Locust extension as a Final Project, an improvement over the [MQTT Malaria](https://github.com/remakeelectric/mqtt-malaria) tool we had previously used.

## Installing MQTT Locust

Install MQTT Locust from the [MQTT Locust](https://github.com/CWRU-Connected-Devices/mqtt-locust) fork in our repository, and install the required dependencies:

```bash
$load cd ~
$load git clone git@github.com:CWRU-Connected-Devices/mqtt-locust.git
$load cd mqtt-locust
$load sudo pip3 install -r requirements.txt
```

## MQTT Locust TaskSets

MQTT Locust uses the same infrastructure to define tasks as Locust.

Here is a sample from the repository:

```python
import json
import random
import resource

from locust import TaskSet, task

from mqtt_locust import MQTTLocust

resource.setrlimit(resource.RLIMIT_NOFILE, (999999, 999999))

TIMEOUT = 6
REPEAT = 100


class MyTaskSet(TaskSet):
    @task(1)
    def qos2(self):
        self.client.publish(
                'lamp/set_config', self.payload(), qos=2, timeout=TIMEOUT,
                repeat=REPEAT, name='qos2 publish'
                )

    @task(1)
    def qos1(self):
        self.client.publish(
                'lamp/set_config', self.payload(), qos=1, timeout=TIMEOUT,
                repeat=REPEAT, name='qos1 publish'
                )

    @task(1)
    def qos0(self):
        self.client.publish(
                'lamp/set_config', self.payload(), qos=0, timeout=TIMEOUT,
                repeat=REPEAT, name='qos0 publish'
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
    min_wait = 5000
    max_wait = 15000
```

This publishes LAMPI states to 'lamp/set\_config' with three different, equally weighted tasks, for:

* QoS 0
* QoS 1
* QoS 2

MQTT Locust adds two keyword arguments to the `publish` method:

* `repeat`
* `timeout`

Messages not acknowledged by the MQTT Broker (**mosquitto**, in our case) within the `timeout` keyword argument time interval are recorded as failed within Locust's statistics system.

The `repeat` keyword argument allows the same message to be published `repeat` times (this allows for very rapid message generation).

NOTE: the Locust `name` keyword argument to provide a friendly string for reporting

NOTE: the MQTT messages we are publishing for this demo are to topics that are not associated with any devices on our EC2 broker.

> COMPATIBILITY:  there appear to be a few issues with the current MQTT Locust (and, possibly, with Locust itself):
> **Slow Memory Leak** - while running, MQTT Locust appears to slowly leak memory - suggested work arounds are:
>     * run MQTT Locust on a large EC2 instance (e.g. `t2.small` or `t2.medium`)>     * do not run MQTT Locust for extended periods of time
>     * stop the Locust process between each test run (do not use the "New Test" button in the Web UI)
>     * open an additional SSH session with your locust instance and run `top` to monitor memory usage
>     * if your locust process consumes all memory on your EC2 instance (which can prevent you from killing the process or running any other programs) use the AWS Console to _reboot_ the instance
> **MQTT Client Not Connected** unclear what is causing this [issue](https://github.com/CWRU-Connected-Devices/mqtt-locust/issues/1) but there is a temporary kludge in the code to mitigate it; this should "hide" the issue an prevent it from affecting the tests or results; let the instructor know if you think you are experiencing the issue

## Invoking

MQTT Locust is invoked the same way as normal Locust, except that the `mqtt://` URL scheme must be provided, for example:

```bash
$load sudo locust --host=mqtt://ec2-34-199-57-78.compute-1.amazonaws.com:50001
```

**NOTE:**  DO NOT FORGET THE `:50001` at the end!  By default, the MQTT Locust plugin will use the default MQTT port number (1883).

![](Images/mqtt_locust.png)

## Monitoring the broker

MQTT provides a set of topics that allow you to monitor the broker.

This command will show all the monitoring topics (note that the $ is escaped with a backslash):

```bash
cloud$ mosquitto_sub -v -t \$SYS/# -p 50001
```

See [Mosquitto Man Page](https://mosquitto.org/man/mosquitto-8.html) under "Broker Status" for more information.  The topics `...\load\...` might be of interest...

Next up: [Observing the System Under Load](../12.3_Observing_System_Under_Load/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
