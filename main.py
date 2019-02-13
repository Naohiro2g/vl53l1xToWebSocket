#!/usr/bin/env python

import signal

import os
import time
from datetime import datetime

import json
import uuid

from socketIO_client_nexus import SocketIO, LoggingNamespace


import VL53L1X

WS_HOST = os.getenv('WS_HOST', 'localhost')
WS_PORT = os.getenv('WS_PORT', 4444)
POOP_LOCATION = os.getenv('POOP_LOCATION', 'NC')
ID = str(uuid.uuid4())

print("""

Press Ctrl+C to exit.

""")

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.start_ranging(1)

running = True


def exit_handler(signal, frame):
    global running
    running = False
    tof.stop_ranging()  # Stop ranging
    sys.stdout.write("\n")
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)


def on_chiotte_response(self, *args):
    print('on_chiotte_response', args)


def on_connect(self):
    print('[Connected]')


def on_reconnect(self):
    print('[Reconnected]')


def on_disconnect(self):
    print('[Disconnected]')


socketIO = SocketIO(WS_HOST, WS_PORT, LoggingNamespace)
socketIO.on('chiotte_response', on_chiotte_response)

distance_in_mm = 0
while running:
    if(tof.get_distance() != distance_in_mm and 100 <= tof.get_distance() <= 230):
        distance_in_mm = tof.get_distance()
        data = json.dumps(
            {
                "id": ID,
                "gender": POOP_LOCATION,
                "pq": distance_in_mm
            }
        )
        print(data)
        socketIO.emit('chiotte', data)
        time.sleep(0.5)
