#!/usr/bin/python

import serial, time, struct, sys
from hass_influx import *

# SLIP constants
FEND = '\xc0'

if len (sys.argv) != 4:
	print "Usage: ... <serial_port> <influx_host> <influx_db>"
	sys.exit(0)

i = hass_influx(inf_host=sys.argv[2], inf_db=sys.argv[3])

print sys.argv[1]
ser = serial.Serial(sys.argv[1], 9600, timeout=0, parity=serial.PARITY_NONE)

def parse(pkt):
	#print "".join("{:02x}".format(ord(c)) for c in pkt)
	#print len(pkt)
	if len(pkt) == 99:
		# Parse known fields; three phase voltages and frequency
		ts = time.time()
		id_number = pkt[0:16]
		[import_wh] = struct.unpack("<Q", pkt[16:24])
		[import_w] = struct.unpack("<i", pkt[48:52])
		[p1, p2, p3] = struct.unpack("<iii", pkt[70:82])
		[v1, v2, v3] = struct.unpack("<HHH", pkt[82:88])
		[i1, i2, i3] = struct.unpack("<hhh", pkt[88:94])
		[f] = struct.unpack("<H", pkt[94:96])

		# Post to InfluxDB
		i.post_influx("voltage", "aidon_p1", "%.01f" % (v1/10.0), ts=ts)
		i.post_influx("voltage", "aidon_p2", "%.01f" % (v2/10.0), ts=ts)
		i.post_influx("voltage", "aidon_p3", "%.01f" % (v3/10.0), ts=ts)
		i.post_influx("current", "aidon_p1", "%.01f" % (i1/10.0), ts=ts)
		i.post_influx("current", "aidon_p2", "%.01f" % (i2/10.0), ts=ts)
		i.post_influx("current", "aidon_p3", "%.01f" % (i3/10.0), ts=ts)
		i.post_influx("power", "aidon", "%.03f" % (import_w/1000.0), ts=ts)
		i.post_influx("energy", "aidon", "%.03f" % (import_wh/1000.0), ts=ts)

		print "Success, %.3f kWh, %.3f W" % (import_wh/1000.0, import_w/1000.0)
	else:
		print "Length mismatch"

buf = ""
while(1):
	if ser.inWaiting():
		buf += ser.read(200)
		if FEND in buf:
			# Split message at the SLIP FEND character
			[pkt, buf] = buf.split(FEND)
			# Replace escape sequences in SLIP message
			pkt = pkt.replace("\xdb\xdc", "\xc0")
			pkt = pkt.replace("\xdb\xdd", "\xdb")
			parse(pkt)
	time.sleep(0.01)
