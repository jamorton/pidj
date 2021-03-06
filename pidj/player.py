
from models import *
import gevent
from app import gs
import datetime
from gevent import socket

def log(s):
	return
	print s

class MPDClient(object):
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = None
		self.port = None

	def close(self):
		try:
			self.socket.close()
		except:
			pass

	def _reconn(self):
		self.socket.connect((self.host, self.port))
		self.read_until("\n")

	def _tryfunc(self, f, *args, **kwargs):
		try:
			return f(*args, **kwargs)
		except IOError:
			self.close()
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._reconn()
			return f(*args, **kwargs)

	def connect(self, host = "localhost", port = 6600):
		self.host = host
		self.port = int(port)
		self._reconn()

	def send(self, msg):
		return self._tryfunc(self.socket.send, msg)

	def recv(self, amt):
		return self._tryfunc(self.socket.recv, amt)

	def read_until(self, delim):
		data = ""
		while 1:
			data += self.recv(1024)
			if data.endswith(delim):
				return data[:-len(delim)]

	def status(self):
		self.send("status\n")
		data = self.read_until("OK\n")
		d = {}
		for line in data.split("\n"):
			i = line.split(": ")
			if len(i) < 2:
				continue
			d[i[0]] = i[1]
		return d

	def clear(self):
		self.send("clear\n")
		self.read_until("OK\n")

	def consume(self, v):
		self.send("consume " + str(v) + "\n")
		self.read_until("OK\n")

	def play(self):
		self.send("play\n")
		self.read_until("OK\n")

	def add(self, song):
		self.send("add " + song + "\n")
		self.read_until("OK\n")

class Player(object):
	def __init__(self):
		self.client = None

	def reconnect(self):
		if self.client:
			self.client.close()
		self.client = MPDClient()
		self.client.connect()
		self.client.clear()
		self.client.consume(1)

	def addSongInner(self, r):
		self.client.add(r["result"]["url"])
		self.client.play()

	def addSong(self, song):
		if not gs.has_init:
			gs.init()
		r = gs.api("getSubscriberStreamKey", {"songID": song.song_id})
		try:
			self.addSongInner(r)
		except ConnectionError:
			self.reconnect()
			self.addSongInner(r)

	def start(self):
		self.reconnect()
		curSong = None
		curUpdated = False

		sp = Song.getPlaying()
		if sp is not None:
			sp.delete()

		while 1:

			if curSong == None:
				log("curSong == none")
				song = Song.getNext()
				if song is not None:
					log("found song")
					self.addSong(song)
					curUpdated = False
					curSong = song
					gevent.sleep(1.0)
				else:
					log("no next song found")
					gevent.sleep(3.0)

			else:
				log("curSong != None")

				if not curUpdated:
					log("curUpdated = false")
					s = self.client.status()

					if "time" in s and s["playlistlength"] == "1" and s["time"] != "0:0":

						duration = int(s["time"].split(":")[1])
						print s

						curSong.duration = duration
						curSong.status = STATUS_PLAYING
						curSong.finish = datetime.datetime.now() \
							+ datetime.timedelta(seconds=duration) \
							- datetime.timedelta(seconds=float(s["elapsed"]))
						curSong.save()
						curUpdated = True

						sleep = (curSong.finish - datetime.datetime.now()).total_seconds() - 2
						log("Sleeping: " + str(sleep))
						gevent.sleep(sleep)
						curSong.status = STATUS_PLAYED
						curSong.save()

						song = Song.getNext()
						if song is not None:
							log("Next song")
							self.addSong(song)
							curUpdated = False
							curSong = song
						else:
							curSong = None

						gevent.sleep(4.0)
					else:
						gevent.sleep(2.0)

				else:
					log("curUpdated = true")
					gevent.sleep(5.0)

def start():
	p = Player()
	return gevent.spawn(p.start)

if __name__ == "__main__":
	m = MPDClient()
	m.connect("localhost", "6600")
	print m.status()
