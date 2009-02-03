#!/usr/bin/python
# coding=UTF-8
#
# backup-µblog is a little CLI tool for downloading and storing your twits or
# dents.
#
# Author: John Drinkwater, john@nextraweb.com
# Licence: GPL v3
# Licence URL: http://www.gnu.org/licenses/gpl-3.0.html
#
import sys,os.path

__version__ = "0.01"

def printusage():
	print "backup-µblog %s" % __version__
	print "Usage: %s <SERVICE> [LOCATION]" % os.path.basename( __file__ )
	print "Location is optional, defaults to ."
	# http://identi.ca/api/statuses/user_timeline/johndrinkwater.json
	# http://twitter.com/statuses/user_timeline/608663.json
	sys.exit(-1)

if __name__ == '__main__':
	
	username = ""
	password = ""
	location = "."

	if len(sys.argv) > 1:
		URL = sys.argv[1]
		if URL.find('atom'):
			URL = URL.replace('atom', 'json')
		elif URL.find('rss'):
			URL = URL.replace('rss', 'json')
		else:
			# fail?
			pass
		
		if len(sys.argv) > 2:
			location = sys.argv[2]

		location = os.path.realpath( location )
		# location doesn’t end in / (or \ win)


	else:
		printusage()

