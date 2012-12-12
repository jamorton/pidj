
import functools
from flask import jsonify
from app import app

def api_route(action, **options):
	def decorator(fn):
		@functools.wraps(fn)
		def wrapper(*args, **kwargs):
			ret = fn(*args, **kwargs)
			obj = {"status": "success"}
			if ret:
				obj.update(ret)
			return jsonify(obj)
		return app.route("/ajax/" + action, methods=["POST"])(wrapper)
	return decorator
