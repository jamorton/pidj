
__all__ = ["run", "models"]

from gevent import monkey
monkey.patch_all()

import gevent

from app import app
from views import *
import models

from gevent.pywsgi import WSGIServer
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.debug import DebuggedApplication

import os

def run_debug(port):
	global app
	app = DebuggedApplication(app, evalex = True)
	WSGIServer(('', port), app).serve_forever()

def run_production(port):
	global app
	app = SharedDataMiddleware(app, {
			'/': os.path.join(os.path.dirname(__file__), 'static')
	})
	WSGIServer(('', port), app).serve_forever()

def run(port):

	import player
	g1 = player.start()

	if app.config["DEBUG"]:
		g2 = gevent.spawn(run_debug, port)
	else:
		g2 = gevent.spawn(run_production, port)

	gevent.joinall([g1, g2])
