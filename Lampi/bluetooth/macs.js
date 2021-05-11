const fs = require('fs');

const STORAGE = `${__dirname}/macs.json`;

function read() {
    try {
        const raw = fs.readFileSync(STORAGE);
        const parsed = new Set(JSON.parse(raw));
        return parsed;
    } catch (e) {
        return new Set();
    }
}

function write(allowed = []) {
    fs.writeFileSync(STORAGE, JSON.stringify([...allowed]));
}

function isAllowed(addr) {
    return read().has(addr);
}

function saveAddress(addr) {
    const saved = read();
    saved.add(addr);
    write(saved);
}

function clear() {
    write([]);
}

module.exports = {
    isAllowed,
    saveAddress,
    clear,
};
