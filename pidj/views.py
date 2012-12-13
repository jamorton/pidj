
from app import app, gs
from models import *
from flask import render_template, request, session
from util import api_route

import requests
import facebook

def get_graph_api(reset = False):

	if not reset and "fb_access_token" in session:
		return facebook.GraphAPI(session["fb_access_token"])

	user = facebook.get_user_from_cookie(
		request.cookies,
		app.config["FACEBOOK_APP_ID"],
		app.config["FACEBOOK_APP_SECRET"]
	)

	if not user:
		return None

	session["fb_access_token"] = user["access_token"]
	return facebook.GraphAPI(session["fb_access_token"])


@app.route('/')
def index():
	return render_template("index.html", app_id = app.config["FACEBOOK_APP_ID"])

@api_route("search")
def ajax_search():
	res = requests.get("http://tinysong.com/s/%s?format=json&limit=20&key=%s" %
					   (request.form["query"], app.config["TINYSONG_KEY"]))
	return {"songs": res.json}

@api_route("queue")
def ajax_queue():
	q = Song.select().where(Song.status == STATUS_QUEUED).order_by(Song.added)
	obj = {"songs": [s.serialize() for s in q]}

	try:
		obj["playing"] = Song.select().where(Song.status == STATUS_PLAYING).order_by(Song.added.desc()).get().serialize()
	except Song.DoesNotExist:
		pass

	return obj

@api_route("add")
def ajax_add():
	songid = request.form["songid"]

	graph = get_graph_api()

	if not graph:
		return {"status": "error", "error": "no facebook user"}

	try:
		profile = graph.get_object("me")
	except facebook.GraphAPIError:
		graph = get_graph_api(True)
		profile = graph.get_object("me")

	sinfo = gs.api("getSongsInfo", {"songIDs": [songid]})
	songs = sinfo["result"]["songs"]

	if len(songs) == 0:
		return {"status": "error", "error": "song not found in database"}

	song = songs[0]

	song = Song(
		user_id = profile["id"],
		user_name = profile["name"],
		song_name = song["SongName"],
		song_id = song["SongID"],
		album_name = song["AlbumName"],
		album_id = song["AlbumID"],
		artist_name = song["ArtistName"],
	)

	song.save()

	return song.serialize()
