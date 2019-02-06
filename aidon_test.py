#!/usr/bin/python

import serial, time, sys
from hass_influx import *
from aidon_obis import *

if len (sys.argv) != 2:
	print "Usage: ... <serial_port>"
	sys.exit(0)

def aidon_callback(fields):
	print fields

ser = serial.Serial(sys.argv[1], 2400, timeout=0.05, parity=serial.PARITY_NONE)
a = aidon(aidon_callback)

while(1):
	while ser.inWaiting():
		a.decode(ser.read(1))
	time.sleep(0.01)

