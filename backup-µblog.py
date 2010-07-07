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
import sys,os.path, simplejson as json, httplib, urllib, urllib2, time, codecs

httplib.HTTPConnection.debuglevel = 1

__version__ = "0.01"

def printusage():
	print "backup-µblog %s" % __version__
	print "Usage: %s <SERVICE> <USER> [LOCATION]" % os.path.basename( __file__ )
	print "Service can be either twitter.com or identi.ca"
	print "User is your handle on that service, without the @"
	print "Location is optional, defaults to ."
	sys.exit(-1)

if __name__ == '__main__':
	
	API = {"identi.ca": "http://identi.ca/api/statuses/user_timeline/%s.json",
			"twitter.com": "http://api.twitter.com/1/statuses/user_timeline/%s.json" }
	noticeURL = { "identi.ca":"http://identi.ca/notice/%(id)d\n", 
				"twitter.com": "http://twitter.com/%(name)s/status/%(id)d\n"}

	location = "."
	
	if len(sys.argv) > 2:

		# twitter.com or identi.ca
		service = sys.argv[1]
		username = sys.argv[2]
		try:
			URL = API.get( service ) % username
		except:
			# We don’t support generic StatusNet services yet.
			print "Service not supported."
			sys.exit(-1)

		# We default to ‘.’
		if len(sys.argv) > 3:
			location = sys.argv[3]

		location = os.path.realpath( location )
		# location doesn’t end in / (or \ win)

		# loop here until end!
		requestednotices = 44
		totalnotices = 0
		requestedpage = 1
		receivednotices = requestednotices


		while receivednotices >= requestednotices:
			# fetch data
			noticedata = ""
			try:
				params = urllib.urlencode( { "count": requestednotices, "page": requestedpage } )
				request = urllib2.Request( "%s?%s" % (URL, params) )
				request.add_header('User-Agent', "Backup µBlog %s %s" % (__version__, ""))
				# can’t do this without something like: data = gzip.GzipFile(fileobj=f).read()
				# request.add_header('Accept-encoding', 'gzip')
				requester = urllib2.build_opener()
				noticedata = requester.open(request).read()
			except:
				print "Failed"
				sys.exit(-1)

			# how does this fail?
			notices = json.loads(noticedata)
		
			# loop notices, make files
			for notice in notices:

				notice['timestamp'] = time.strptime( notice['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
				notice['filename']  = unicode( os.path.join( location, time.strftime( "%FT%H%M%SZ", notice['timestamp'] ) ), encoding='utf-8', errors='ignore' )

				print "Writing: %s %s" % ( os.path.basename( notice['filename'] ), notice['text'] )
				# test if file exists, if so, fail? (we’ve already backed this up)
				file = codecs.open( notice['filename'], encoding='utf-8', mode='w+' )

				file.write( "From: \"%s\" <%s@%s>\n" % ( notice['user']['name'], notice['user']['screen_name'], service ) )
				file.write( "To: \"John Drinkwater\" <johndrinkwater@%s>\n" % (service) )
				file.write( "Subject: %s\n" % notice['text'][:60] )

				file.write( "Message-ID: <%d@notice.%s>\n" % (notice['id'], service) )
				file.write( "Date: %s\n" % time.strftime( "%a, %d %b %Y %H:%M:%S +0000", notice['timestamp'] ) )

				file.write( "URI: %s\n" % noticeURL.get(service) % ({'name': username, 'id':notice['id']}) )

				file.write( "Source: %s\n" % notice['source'] )

				# geo
				if notice['geo'] is not None:
					if notice['geo']['type'] == u'Point':
						file.write( "Geolocation: %s\n" % notice['geo']['coordinates'] )
					else:
						print "Unsupported geo entry '" + notice['geo']['type'] + "'"

				file.write( "Truncated: %s\n" % notice['truncated'] )
				file.write( "Favourited: %s\n" % notice['favorited'] )

				# part of a conversation.
				if notice['in_reply_to_status_id'] is not None:
					file.write( "In-Reply-To: <%d@notice.%s>\n" % (notice['in_reply_to_status_id'], service) )
				if notice['in_reply_to_user_id'] is not None:
					file.write( "In-Reply-To-User: %s@%s\n" % (notice['in_reply_to_screen_name'], service) )

				#retweeted
				try:
					if notice['retweeted_status'] is not None:
						file.write( "Resent-Sender: \"%s\" <%s@%s>\n" % ( notice['retweeted_status']['user']['name'], notice['retweeted_status']['user']['screen_name'], service ) )
						file.write( "Resent-Message-ID: <%d@notice.%s>\n" % (notice['retweeted_status']['id'], service) )
				except:
					pass				

				file.write( "\n" )
				file.write( "%s\n" % notice['text'] )
				file.close()

			# increment
			receivednotices = len(notices)
			requestedpage = requestedpage + 1
			totalnotices = totalnotices + receivednotices
			print "Backed up %d dents so far. [%d/%d]" % (totalnotices, receivednotices, requestednotices)

			# sleep here for a little
			print "Pausing to throttle hitting the server."
			time.sleep( 15 )

	else:
		printusage()

