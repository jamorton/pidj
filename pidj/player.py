
from models import *
import gevent
from mpd import MPDClient, ConnectionError
from app import gs
import datetime

def log(s):
	return
	print s

class Player(object):
	def __init__(self):
		pass

	def reconnect(self):
		self.client = MPDClient()
		self.client.connect(host="localhost", port="6600")
		self.client.clear()
		self.client.consume(1)

	def addSong(self, song, redo = False):
		if not gs.has_init:
			gs.init()
		r = gs.api("getSubscriberStreamKey", {"songID": song.song_id})
		try:
			self.client.add(r["result"]["url"])
			self.client.play()
		except ConnectionError:
			if redo:
				self.reconnect()
				self.addSong(song, True)


	def start(self):
		self.reconnect()
		curSong = None
		curUpdated = False

		sp = Song.getPlaying()
		if sp is not None:
			sp.delete()

		while 1:

			log("loop")

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
