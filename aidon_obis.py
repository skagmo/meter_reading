# Aidon AMS meter parser, specifically for OBIS messages used by Hafslund meters
# Needs crcmod (sudo pip install crcmod)

import struct, crcmod

# HDLC constants
FLAG = '\x7e'
ESCAPE = '\x7d'

# HDLC states
WAITING = 0
DATA = 1
ESCAPED = 2

# Number of objects in known frames
OBJECTS_2P5SEC = 1
OBJECTS_10SEC = 12
OBJECTS_1HOUR = 17

# OBIS types
TYPE_STRING = 0x0a
TYPE_UINT32 = 0x06
TYPE_INT16 = 0x10
TYPE_OCTETS = 0x09
TYPE_UINT16 = 0x12

class aidon:
	def __init__(self, callback):
		self.state = WAITING
		self.pkt = ""
		self.crc_func = crcmod.mkCrcFun(0x11021, rev=True, initCrc=0xffff, xorOut=0x0000)
		self.callback = callback

	# Does a lot of assumptions on Aidon/Hafslund COSEM format
	# Not a general parser! 
	def parse(self, pkt):

		# 0,1 frame format
		# 2 client address
		# 3,4 server address
		# 5 control
		# 6,7 HCS
		# 8,9,10 LLC

		frame_type = (ord(pkt[0]) & 0xf0) >> 4
		length = ((ord(pkt[0]) & 0x07) << 8) + ord(pkt[1])
		object_count = ord(pkt[18])
		pkt = pkt[19:] # Remove 18 first bytes to start with first object

		fields = {}

		# If number of objects doesn't match any known type, don't continue
		if not (object_count in [OBJECTS_2P5SEC, OBJECTS_10SEC, OBJECTS_1HOUR]):
			return

		# Fill array with objects
		data = []
		for j in range(0, object_count):
			dtype = ord(pkt[10])
			
			if (dtype == TYPE_STRING):
				size = ord(pkt[11])
				data.append(pkt[12:12+size])
				pkt = pkt[12+size:]

			elif (dtype == TYPE_UINT32):
				data.append(struct.unpack(">I", pkt[11:15])[0])
				pkt = pkt[21:]

			elif (dtype == TYPE_INT16):
				data.append(struct.unpack(">h", pkt[11:13])[0])
				pkt = pkt[19:]

			elif (dtype == TYPE_OCTETS):
				size = ord(pkt[11])
				data.append(pkt[12:12+size])
				pkt = pkt[12+size:]

			elif (dtype == TYPE_UINT16):
				data.append(struct.unpack(">H", pkt[11:13])[0])
				pkt = pkt[19:]

			else:
				return # Unknown type, cancel
	
		# Convert array with generic types to dictionary with sensible keys
		if (len(data) == OBJECTS_2P5SEC):
			fields['p_act_in'] = data[0]
		
		elif (len(data) == OBJECTS_10SEC) or (len(data) == OBJECTS_1HOUR):
			fields['version_id'] = data[0]
			fields['meter_id'] = data[1]
			fields['meter_type'] = data[2]
			fields['p_act_in'] = data[3]
			fields['p_act_out'] = data[4]
			fields['p_react_in'] = data[5]
			fields['p_react_out'] = data[6]
			fields['il1'] = data[7] / 10.0
			fields['il2'] = data[8] / 10.0
			fields['ul1'] = data[9] / 10.0
			fields['ul2'] = data[10] / 10.0
			fields['ul3'] = data[11] / 10.0

			if (len(data) == OBJECTS_1HOUR):
				fields['energy_act_in'] = data[13] / 100.0
				fields['energy_act_out'] = data[14] / 100.0
				fields['energy_react_in'] = data[15] / 100.0
				fields['energy_react_out'] = data[16] / 100.0

		self.callback(fields)

	# General HDLC decoder
	def decode(self, c):
		# Waiting for packet start
		if (self.state == WAITING): 
			if (c == FLAG):
				self.state = DATA
				self.pkt = ""

		elif (self.state == DATA):
			if (c == FLAG):
				# Minimum length check
				if (len(self.pkt) >= 19):
					# Check CRC
					crc = self.crc_func(self.pkt[:-2])
					crc ^= 0xffff
					if (crc == struct.unpack("<H", self.pkt[-2:])[0]):
						self.parse(self.pkt)
				self.pkt = ""
			elif (c == ESCAPE):
				self.state = ESCAPED
			else:
				self.pkt += c

		elif (self.state == ESCAPED):
			self.pkt += chr(ord(c) ^ 0x20)
			self.state = DATA

