
from flask import Flask
from flask_peewee.db import Database
import config
import grooveshark

app = Flask(__name__)
app.config.from_envvar("PIDJ_SETTINGS")

db = Database(app)
gs = grooveshark.Client(app)
