# Needs crcmod (sudo pip install crcmod)

import struct, crcmod

FLAG = '\x7e'
ESCAPE = '\x7d'
	
WAITING = 0	
DATA = 1
ESCAPED = 2

LONG_FRAME_OBJECTS = 12

TYPE_STRING = 0x0a
TYPE_UINT32 = 0x06
TYPE_INT16 = 0x10
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
		# 11-16
		frame_type = (ord(pkt[0]) & 0xf0) >> 4
		length = ((ord(pkt[0]) & 0x07) << 8) + ord(pkt[1])

		object_count = ord(pkt[18])
		pkt = pkt[19:] # Remove 18 first bytes to start with first object

		fields = {}

		if (object_count == LONG_FRAME_OBJECTS):
			data = []

			for j in range(0, LONG_FRAME_OBJECTS):
				dtype = ord(pkt[10])
				
				if (dtype == TYPE_STRING): 
					strlen = ord(pkt[11])
					data.append(pkt[12:12+strlen])
					pkt = pkt[12+strlen:]

				elif (dtype == TYPE_UINT32): 
					data.append(struct.unpack(">I", pkt[11:15])[0])
					pkt = pkt[21:]

				elif (dtype == TYPE_INT16): 
					data.append(struct.unpack(">h", pkt[11:13])[0])
					pkt = pkt[19:]

				elif (dtype == TYPE_UINT16): 
					data.append(struct.unpack(">H", pkt[11:13])[0])
					pkt = pkt[19:]

				else:
					return # Unknown field
	
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

			self.callback(fields)

		elif (object_count == 1) and (len(pkt) == 23):
			dtype = ord(pkt[10])
			if (dtype == TYPE_UINT32):
				fields['p_act_in'] = struct.unpack(">I", pkt[11:15])[0]
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

