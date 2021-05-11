import os
import json

FILE = "bluetooth/macs.json"

def _read():
    raw = "[]"

    try:
        with open(FILE, 'r') as f:
            raw = f.read()
    except FileNotFoundError:
        pass

    return json.loads(raw)

def _write(allowed):
    with open(FILE, 'w') as f:
        f.write(json.dumps(allowed))

def isAllowed(addr):
    return (addr in _read())

def saveAddress(addr):
    saved = _read()
    saved.append(addr)
    _write(saved)

def clear():
    _write([])
