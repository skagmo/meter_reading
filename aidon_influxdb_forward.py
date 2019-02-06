#!/usr/bin/python

import serial, time, sys
from hass_influx import *
from aidon_obis import *

if len (sys.argv) != 4:
	print "Usage: ... <serial_port> <influx_host> <influx_db>"
	sys.exit(0)

i = hass_influx(inf_host=sys.argv[2], inf_db=sys.argv[3])
ser = serial.Serial(sys.argv[1], 2400, timeout=0.05, parity=serial.PARITY_NONE)

def aidon_callback(fields):
	ts = time.time()
	if 'p_act_in' in fields:
		i.post_influx("power", "aidon", "%.03f" % (fields['p_act_in']/1000.0), ts=ts)

	if 'il1' in fields:
		i.post_influx("voltage", "aidon_p1", "%.01f" % fields['ul1'], ts=ts)
		i.post_influx("voltage", "aidon_p2", "%.01f" % fields['ul2'], ts=ts)
		i.post_influx("voltage", "aidon_p3", "%.01f" % fields['ul3'], ts=ts)
		i.post_influx("current", "aidon_p1", "%.01f" % fields['il1'], ts=ts)
		i.post_influx("current", "aidon_p2", "%.01f" % fields['il2'], ts=ts)

a = aidon(aidon_callback)
				
while(1):
	while ser.inWaiting():
		a.decode(ser.read(1))
	time.sleep(0.01)

