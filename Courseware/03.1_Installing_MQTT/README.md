# Installing Mosquitto MQTT Broker

### MQTT
[MQTT](http://mqtt.org/) is a "machine-to-machine (M2M) / Internet of Things (IoT) connectivity protocol."  It uses a Publish/Subscribe (aka Pub/Sub) communications model.  All clients, whether publishing or subscribing to message topics, connect to a broker.

We will be using the Open Source [Mosquitto](http://mosquitto.org/) MQTT broker.

### Installing MQTT


Installing:

```
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients -y
```

After that completes, the mosquitto broker should be installed and running. You can verify that with the "service" tool:

```
pi@raspberrypi:~ $ service mosquitto status
● mosquitto.service - Mosquitto MQTT v3.1/v3.1.1 Broker
   Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; vendor preset
   Active: active (running) since Sat 2021-01-30 16:46:20 GMT; 1min 23s ago
     Docs: man:mosquitto.conf(5)
           man:mosquitto(8)
 Main PID: 5390 (mosquitto)
    Tasks: 1 (limit: 2063)
   CGroup: /system.slice/mosquitto.service
           └─5390 /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
```

or with the "ps" command:

```
pi@raspberrypi:~ $ ps -A | grep mosquitto
 5390 ?        00:00:00 mosquitto
```
Note: For those new to Unix, that shows the mosquitto broker is running with Process ID (aka "pid") 5390.


Next up: go to [Mosquitto Tools](../03.2_Mosquitto_Tools/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
