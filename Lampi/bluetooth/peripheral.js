#! /usr/bin/env node
const fs = require('fs');
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

var mqtt_options = {
    clientId: mqtt_clientId,
}

var mqtt_client = mqtt.connect('mqtt://localhost', mqtt_options);

const BLACKLIST_TOPIC = 'lamp/bluetooth/blacklist';
const NEW_MAC_TOPIC = 'lamp/bluetooth/new';

mqtt_client.on('connect', () => {
    mqtt_client.subscribe('lamp/bluetooth/blacklist');
});

mqtt_client.on('message', (topic, message) => {
    console.log(topic);
    console.log(message.toString());
});

const MACS_FILE = `${__dirname}/macs.json`;
const BADS_FILE = `${__dirname}/banned.json`;

function getSavedAddresses() {
    let raw = "[]";

    try {
        raw = fs.readFileSync(MACS_FILE);
    } catch (e) {
        fs.writeFileSync(MACS_FILE, raw);
    }

    return new Set(JSON.parse(raw));
}

function getBlacklistedAddresses() {
    let raw = "[]";

    try {
        raw = fs.readFileSync(BADS_FILE);
    } catch (e) {
        fs.writeFileSync(BADS_FILE, raw);
    }

    return new Set(JSON.parse(raw));
}

function saveNewAddress(addr) {
    let all = getSavedAddresses();
    all.add(addr);
    fs.writeFileSync(MACS_FILE, JSON.stringify([...all]));
    mqtt_client.publish(NEW_MAC_TOPIC, addr);
}

function blacklistAddress(addr) {
    let bad = getBlacklistedAddresses();
    bad.add(addr);
    fs.writeFileSync(BADS_FILE, JSON.stringify([...bad]));

    if (addr == bt_clientAddress) {
        bleno.disconnect();
    }
}

bleno.on('stateChange', function(state) {
  if (state === 'poweredOn') {
    bleno.startAdvertising('LampiService', [lampiService.uuid, deviceInfoService.uuid], function(err)  {
      if (err) console.log(err);
    });
  } else {
    bleno.stopAdvertising();
    console.log('not poweredOn');
  }
});


bleno.on('advertisingStart', function(err) {
  if (!err) {
    console.log('advertising...');
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

    const blacklisted = getBlacklistedAddresses();
    const saved = getSavedAddresses();

    if (blacklisted.has(clientAddress)) {
        console.log(`Blacklisted client ${clientAddress} rejected`);
        bleno.disconnect();
        return;
    } else if (!saved.has(clientAddress)) {
        console.log('Storing new address', clientAddress);
        saveNewAddress(clientAddress);
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
    bt_clientAddress = null;
    bt_lastRssi = 0;
});

