#!/usr/bin/python

import serial, time, struct, sys

# SLIP constants
FEND = '\xc0'

def parse(pkt):
    print "".join("{:02x}".format(ord(c)) for c in pkt)
    print len(pkt)
    pkt = pkt[len(pkt)-79:]
    if len(pkt) == 79:
        # Parse known fields; three phase voltages and frequency
        [v1, v2, v3] = struct.unpack("<HHH", pkt[62:68])
        [f] = struct.unpack("<H", pkt[74:76])
        print "v1=%.1f v2=%.1f v3=%.1f f=%.2f" % (v1/10.0, v2/10.0, v3/10.0, f/100.0)

        # Unknown fields
        [u1] = struct.unpack("<H", pkt[20:22])
        [u2] = struct.unpack("<H", pkt[28:30])
        [u3] = struct.unpack("<H", pkt[40:42])
        [u4] = struct.unpack("<H", pkt[44:46])
        [u5, u6] = struct.unpack("<HH", pkt[48:52])
        [u7] = struct.unpack("<H", pkt[58:60])
        print u1, u2, u3, u4, u5, u6, u7
    else:
        print "Length mismatch"


if len (sys.argv) != 2:
    print "Missing port argument"
    sys.exit(0)

buf = ""
ser = serial.Serial(sys.argv[1], baudrate=9600, timeout=0, parity=serial.PARITY_NONE)

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

