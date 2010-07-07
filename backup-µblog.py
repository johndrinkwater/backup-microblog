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
		if URL.find('atom') is not -1:
			URL = URL.replace('atom', 'json')
		elif URL.find('rss') is not -1:
			URL = URL.replace('rss', 'json')
		else:
			# fail?
			pass

		if len(sys.argv) > 2:
			location = sys.argv[2]

		location = os.path.realpath( location )
		# location doesn’t end in / (or \ win)

		# loop here until end!
		requestednotices = 44
		totalnotices = 0
		requestedpage = 1
		receivednotices = requestednotices


		while receivednotices > 0:
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

				file.write( "From: \"%s\" <%s@identi.ca>\n" % ( notice['user']['name'], notice['user']['screen_name'] ) )
				file.write( "To: \"John Drinkwater\" <johndrinkwater@identi.ca>\n" )
				file.write( "Subject: %s\n" % notice['text'][:60] )

				file.write( "Message-ID: <%d@notice.identi.ca>\n" % notice['id'] )
				file.write( "Date: %s\n" % time.strftime( "%a, %d %b %Y %H:%M:%S +0000", notice['timestamp'] ) )
				# this is hardcoded, until we add service pulling from dir.laconi.ca
				file.write( "URI: http://identi.ca/notice/%d\n" % notice['id'] )
				#file.write( "URI: http://twitter.com/johndrinkwater/status/%d\n" % notice['id'] )
				file.write( "Source: %s\n" % notice['source'] )
				# Contained within Date, though in RFC 2822 format
				# file.write( "Posted: %s\n" % time.strftime( "%FT%H:%M:%SZ", notice['timestamp'] ) )

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
					file.write( "In-Reply-To: <%d@notice.identi.ca>\n" % notice['in_reply_to_status_id'] )
				if notice['in_reply_to_user_id'] is not None:
					file.write( "In-Reply-To-User: %s@identi.ca\n" % notice['in_reply_to_screen_name'] )

				#retweeted
				try:
					if notice['retweeted_status'] is not None:
						file.write( "Resent-Sender: \"%s\" <%s@identi.ca>\n" % ( notice['retweeted_status']['user']['name'], notice['retweeted_status']['user']['screen_name'] ) )
						file.write( "Resent-Message-ID: <%d@notice.identi.ca>\n" % notice['retweeted_status']['id'] )
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

