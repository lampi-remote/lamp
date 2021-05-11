var util = require('util');
var bleno = require('bleno');

var CHARACTERISTIC_NAME = 'Preset';

var LampiPresetCharacteristic = function (lampiState) {
    LampiPresetCharacteristic.super_.call(this, {
        uuid: '0005A7D3-D8A4-4FEA-8174-1736E808C066',
        properties: ['read', 'write', 'notify'],
        secure: [],
        descriptors: [
            new bleno.Descriptor({
                uuid: '2901',
                value: CHARACTERISTIC_NAME,
            }),
            new bleno.Descriptor({
                uuid: '2904',
                value: new Buffer([0x04, 0x00, 0x27, 0x00, 0x01, 0x00, 0x00])
            }),
        ],
    });

    this._update = null;

    this.changed_preset = function (curr_num, new_num) {
        console.log('lampiState changed LampiPresetCharacteristic');
        if (this._update !== null) {
            console.log('this._update is ', typeof (this._update));
            console.log('updating new preset uuid=', this.uuid);
            var data = new Buffer(1);
            console.log(curr_num);
            console.log(new_num);
            if (curr_num == new_num) {
                data.writeUInt8(0x0, 0);
            } else {
                data.writeUInt8(new_num);
            }
            this._update(data);
        }
    }

    this.lampiState = lampiState;

    this.lampiState.on('changed_preset', this.changed_preset.bind(this));

}

util.inherits(LampiPresetCharacteristic, bleno.Characteristic);

LampiPresetCharacteristic.prototype.onReadRequest = function (offset, callback) {
    console.log('onReadRequest');
    if (offset) {
        console.log('onReadRequest offset');
        callback(this.RESULT_ATTR_NOT_LONG, null);
    } else {
        var data = new Buffer(1);
        data.writeUInt8(this.lampiState.preset_num, 0);

        console.log('onReadRequest returning ', data);
        callback(this.RESULT_SUCCESS, data);
    }
};

LampiPresetCharacteristic.prototype.onWriteRequest = function (data, offset, withoutResponse, callback) {
    if (offset) {
        callback(this.RESULT_ATTR_NOT_LONG);
    } else if (data.length !== 1) {
        callback(this.RESULT_INVALID_ATTRIBUTE_LENGTH);
    } else {
        var new_preset = data.readUInt8(0);
        this.lampiState.set_preset(new_preset);
        callback(this.RESULT_SUCCESS);
    }
};

LampiPresetCharacteristic.prototype.onSubscribe = function (maxValueSize, updateValueCallback) {
    console.log('subscribe on ', CHARACTERISTIC_NAME);
    this._update = updateValueCallback;
}

LampiPresetCharacteristic.prototype.onUnsubscribe = function () {
    console.log('unsubscribe on ', CHARACTERISTIC_NAME);
    this._update = null;
}

module.exports = LampiPresetCharacteristic;