import requests, time

VERSION = 0.2

class hass_influx:
	def __init__(self, hass_host="", hass_token="", inf_host="", inf_db="", print_post=False):
		self.hass_host = hass_host
		self.hass_s = requests.Session()
		self.hass_s.headers.update({'Authorization': 'Bearer %s' % hass_token})

		self.influx_host = inf_host
		self.influx_db = inf_db

		self.print_post = print_post

	def post_hass(self, hass_id, hass_name, str_value, unit):
		if self.hass_host:
			try:
				ret = self.hass_s.post(
					self.hass_host + "/api/states/sensor.%s" % hass_id, 
					data=("""
					{
						"state": "%s",
						"attributes": {
							"unit_of_measurement": "%s",
							"friendly_name": "%s"
						}
					}
					""" % (str_value, unit, hass_name) ))
				if not (ret.status_code == 200):
					print ret
	
			except Exception as e:
				print hass_id, hass_name, str_value, unit
				print "Failed HASS: %s" % e

	def post_influx(self, meas_type, name, value, ts=time.time()):
		if self.influx_host and self.influx_db:
			post_data = "%s,dev=%s value=%s %u" % \
				(meas_type, name, value, ts*1000000000)	
			status = requests.post(self.influx_host + '/write',
				params={'db': self.influx_db}, 
				data=post_data)
			if self.print_post:
				print post_data

	def post(self, ident, type_, value, hass_name="", hass_unit="", ts=time.time()):
		self.post_influx(type_, ident, value, ts)
		if hass_name:
			self.post_hass(ident + '_' + type_, hass_name, value, hass_unit)
