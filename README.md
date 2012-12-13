
# PiDJ

A crowd-sourced DJ platform that allows anyone in the room to search for
and queue up songs.

Users visit a flask-powered website and can search (using the Grooveshark
api in the backend) and add a song of their choosing to the queue. Songs are played
in FIFO order using mpd. PiDJ is designed to be run on a raspberry pi that is connected
to speakers, although all software used is cross platform and can be run on x86 linux or osx.

## Technology

 * Flask website
 * gevent for IO and player control
 * mpd for music control and streaming
 * Facebook for user auth and identification
 * Grooveshark api for song search and streaming
 * peewee/sqlite for relational database
 * redis for key-value store and song caching
