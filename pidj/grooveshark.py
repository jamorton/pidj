
import hashlib
import hmac
import simplejson
import requests

COUNTRY = {'ID': 221, 'CC1': 0, 'CC2': 0, 'CC3': 0, 'CC4': 0, 'DMA': 0, 'IPR': 0}

class Client(object):
	def __init__(self, app):
		self.key    = app.config["GROOVESHARK_KEY"]
		self.secret = app.config["GROOVESHARK_SECRET"]
		self.user   = app.config["GROOVESHARK_USER"]
		self.passw  = app.config["GROOVESHARK_PASS"]

		self.session = None
		self.has_init = False

		app.before_first_request(lambda: self.init())

	def signature(self, data):
		return hmac.new(self.secret, data).hexdigest()

	def api(self, method, params = {}):
		params["country"] = COUNTRY
		data = {
			"method": method,
			"parameters": params,
			"header": {"wsKey": self.key}
		}
		if self.session is not None:
			data["header"]["sessionID"] = self.session

		data = simplejson.dumps(data)
		sig = self.signature(data)

		r = requests.post("https://api.grooveshark.com/ws3.php?sig=%s" % sig, data = data)
		print r.json

		return r.json

	def init(self):
		if self.has_init:
			return

		response = self.api("startSession")
		if response["result"]["success"] == True:
			self.session = response["result"]["sessionID"]
		else:
			raise Exception("Could not start session")

		response = self.api("authenticate", {
				"login": self.user,
				"password": self.passw
		})
		self.has_init = True
