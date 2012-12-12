
from app import db
from peewee import *
import datetime

__all__ = ["Song", "Vote", "create_tables", "STATUS_PLAYED", "STATUS_PLAYING", "STATUS_QUEUED"]

STATUS_PLAYED, STATUS_PLAYING, STATUS_QUEUED = range(3)

class Song(db.Model):
	user_id = CharField(max_length = 15)
	user_name = CharField(max_length = 100)
	song_name = CharField()
	song_id = IntegerField()
	album_name = CharField()
	album_id = IntegerField()
	artist_name = CharField()
	added = DateTimeField(default = datetime.datetime.now)
	status = IntegerField(default = STATUS_QUEUED)
	finish = DateTimeField(default = datetime.datetime.now)

	def __unicode__(self):
		return self.song_name

	@staticmethod
	def getPlaying():
		try:
			return Song.get(status = STATUS_PLAYING)
		except Song.DoesNotExist:
			return None

	@staticmethod
	def getNext():
		try:
			return Song.select().where(Song.status == STATUS_QUEUED).order_by(Song.added).get()
		except Song.DoesNotExist:
			return None

	def serialize(self):
		return {
			"id": self.id,
			"user_id": self.user_id,
			"user_name": self.user_name,
			"song_name": self.song_name,
			"song_id": str(self.song_id),
			"album_name": self.album_name,
			"album_id": str(self.album_id),
			"artist_name": self.artist_name,
			"added": self.added.isoformat(),
			"status": self.status,
			"finish": self.finish.isoformat(),
			"now": datetime.datetime.now().isoformat()
		}

class Vote(db.Model):
	user_id = CharField(max_length = 15, index = True)
	song = ForeignKeyField(Song)

def create_tables():
	Song.create_table()
	Vote.create_table()
