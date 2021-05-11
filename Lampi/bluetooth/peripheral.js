#! /usr/bin/env node
const macs = require('./macs');

var child_process = require('child_process');
var device_id = child_process.execSync('cat /sys/class/net/eth0/address | sed s/://g').toString().replace(/\n$/, '');

process.env['BLENO_DEVICE_NAME'] = 'LAMPI ' + device_id;

var serviceName = 'LampiService';
var bleno = require('bleno');
var mqtt = require('mqtt');

var LampiState = require('./lampi-state');
var LampiService = require('./lampi-service');
var DeviceInfoService = require('./device-info-service');

var lampiState = new LampiState();
var lampiService = new LampiService( lampiState );
var deviceInfoService = new DeviceInfoService( 'CWRU', 'LAMPI', device_id);

var bt_clientAddress = null;
var bt_lastRssi = 0;

var mqtt_clientId = 'lamp_bt_central';
var mqtt_client_connection_topic = 'lamp/connection/' + mqtt_clientId + '/state';

const NEW_MAC_TOPIC = 'lamp/bluetooth/remote';
const DISCOVERABLE_TOPIC = 'lamp/bluetooth/discovery';
const DISCONNECT_TOPIC = 'lamp/bluetooth/disconnect';

var mqtt_options = {
    clientId: mqtt_clientId,
    will: {
        topic: NEW_MAC_TOPIC,
        payload: null,
        retain: true,
        qos: 2,
    }
}

var isAdvertising = false;
var isDiscoverable = true;

var mqtt_client = mqtt.connect('mqtt://localhost', mqtt_options);

mqtt_client.on('message', (topic, message) => {
    if (topic === DISCOVERABLE_TOPIC) {
        if (message.toString() === "true") {
            if (!isDiscoverable && !isAdvertising) {
                advertise();
            }

            isDiscoverable = true;
        } else {
            if (isDiscoverable && isAdvertising) {
                bleno.stopAdvertising();
                isAdvertising = false;
            }

            isDiscoverable = false;
        }
    } else if (topic === DISCONNECT_TOPIC) {
        bleno.disconnect();
    }
});

mqtt_client.on('connect', () => {
    mqtt_client.subscribe(DISCOVERABLE_TOPIC);
    mqtt_client.subscribe(DISCONNECT_TOPIC);
});

bleno.on('stateChange', function(state) {
  if (state === 'poweredOn') {
    if (isDiscoverable) advertise();
  } else {
    isAdvertising = false;
    bleno.stopAdvertising();
    console.log('not poweredOn');
  }
});

function advertise() {
    bleno.startAdvertising('LampiService', [lampiService.uuid, deviceInfoService.uuid], function(err)  {
      if (err) console.log(err);
    });
}

bleno.on('advertisingStart', function(err) {
  if (!err) {
    console.log('advertising...');
    isAdvertising = true;
    bleno.setServices([
        lampiService,
        deviceInfoService,
    ]);
  }
});

function updateRSSI(err, rssi) {
    console.log('RSSI err: ' + err + ' rssi: ' + rssi);
    // if we are still connected
    if (bt_clientAddress) {
        // and large change in RSSI
        if ( Math.abs(rssi - bt_lastRssi) > 2 ) {
            // publish RSSI value to MQTT 
            mqtt_client.publish('lamp/bluetooth', JSON.stringify({
                'client': bt_clientAddress,
                'rssi': rssi,
                }));
        }
        // update our last RSSI value
        bt_lastRssi = rssi;
        // set a timer to update RSSI again in 1 second
        setTimeout( function() {
            bleno.updateRssi( updateRSSI );
            }, 1000);
        }
}

// New device connected
bleno.on('accept', function(clientAddress) {
    console.log('New connection from: ' + clientAddress);

    const status = {
        allowed: macs.isAllowed(clientAddress),
        address: clientAddress,
    };

    if (!status.allowed) {
        mqtt_client.publish(NEW_MAC_TOPIC, JSON.stringify(status));
        bleno.disconnect();
        return;
    } else {
        mqtt_client.publish(NEW_MAC_TOPIC, JSON.stringify(status), { retain: true });
    }

    bt_clientAddress = clientAddress;
    bt_lastRssi = 0;
    mqtt_client.publish('lamp/bluetooth', JSON.stringify({
        state: 'connected',
        'client': bt_clientAddress,
        }));

    bleno.updateRssi( updateRSSI );
});

// On device disconnect
bleno.on('disconnect', function(clientAddress) {
    console.log('disconnect: ' + clientAddress);
    mqtt_client.publish('lamp/bluetooth', JSON.stringify({
        state: 'disconnected',
        'client': bt_clientAddress,
        }));
    mqtt_client.publish(NEW_MAC_TOPIC, null, { retain: true });
    bt_clientAddress = null;
    bt_lastRssi = 0;
});

