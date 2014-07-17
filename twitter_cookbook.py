# -*- coding: utf-8 -*-
"""
Created on Wed May 28 19:54:40 2014

@author: VAUGA026
"""
#%% Example 1. Accessing Twitter's API for development purposes
import twitter
import json


def oauth_login():
    CONSUMER_KEY = '3dJxJpgFlvfdAcaj3IAJLzwR0'
    CONSUMER_SECRET = 'eJTVOU98L5qYmz4m9pnLZFCjAROnJHRBQxxhQ4h22smNySOtDw'
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

twitter_api = oauth_login()    





#%% Example 2. Doing the OAuth dance to access Twitter's API for production purposes
import json
from flask import Flask, request
import multiprocessing
from threading import Timer
from IPython.display import IFrame
from IPython.display import display
from IPython.display import Javascript as JS

import twitter
from twitter.oauth_dance import parse_oauth_tokens
from twitter.oauth import read_token_file, write_token_file

# Note: This code is exactly the flow presented in the _AppendixB notebook

OAUTH_FILE = "resources/ch09-twittercookbook/twitter_oauth"

# XXX: Go to http://twitter.com/apps/new to create an app and get values
# for these credentials that you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information 
# on Twitter's OAuth implementation, and ensure that *oauth_callback*
# is defined in your application settings as shown next if you are 
# using Flask in this IPython Notebook.

# Define a few variables that will bleed into the lexical scope of a couple of 
# functions that follow
CONSUMER_KEY = '3dJxJpgFlvfdAcaj3IAJLzwR0'
CONSUMER_SECRET = 'eJTVOU98L5qYmz4m9pnLZFCjAROnJHRBQxxhQ4h22smNySOtDw'
oauth_callback = 'http://127.0.0.1:5000/oauth_helper'
    
# Set up a callback handler for when Twitter redirects back to us after the user 
# authorizes the app

webserver = Flask("TwitterOAuth")
@webserver.route("/oauth_helper")
def oauth_helper():
    
    oauth_verifier = request.args.get('oauth_verifier')

    # Pick back up credentials from ipynb_oauth_dance
    oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)
    
    _twitter = twitter.Twitter(
        auth=twitter.OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        format='', api_version=None)

    oauth_token, oauth_token_secret = parse_oauth_tokens(
        _twitter.oauth.access_token(oauth_verifier=oauth_verifier))

    # This web server only needs to service one request, so shut it down
    shutdown_after_request = request.environ.get('werkzeug.server.shutdown')
    shutdown_after_request()

    # Write out the final credentials that can be picked up after the following
    # blocking call to webserver.run().
    write_token_file(OAUTH_FILE, oauth_token, oauth_token_secret)
    return "%s %s written to %s" % (oauth_token, oauth_token_secret, OAUTH_FILE)

# To handle Twitter's OAuth 1.0a implementation, we'll just need to implement a 
# custom "oauth dance" and will closely follow the pattern defined in 
# twitter.oauth_dance.

def ipynb_oauth_dance():
    
    _twitter = twitter.Twitter(
        auth=twitter.OAuth('', '', CONSUMER_KEY, CONSUMER_SECRET),
        format='', api_version=None)

    oauth_token, oauth_token_secret = parse_oauth_tokens(
            _twitter.oauth.request_token(oauth_callback=oauth_callback))

    # Need to write these interim values out to a file to pick up on the callback 
    # from Twitter that is handled by the web server in /oauth_helper
    write_token_file(OAUTH_FILE, oauth_token, oauth_token_secret)
    
    oauth_url = ('http://api.twitter.com/oauth/authorize?oauth_token=' + oauth_token)
    
    # Tap the browser's native capabilities to access the web server through a new 
    # window to get user authorization
    display(JS("window.open('%s')" % oauth_url))

# After the webserver.run() blocking call, start the OAuth Dance that will
# ultimately cause Twitter to redirect a request back to it. Once that request
# is serviced, the web server will shut down and program flow will resume
# with the OAUTH_FILE containing the necessary credentials.
Timer(1, lambda: ipynb_oauth_dance()).start()

webserver.run(host='0.0.0.0')

# The values that are read from this file are written out at
# the end of /oauth_helper
oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)

# These four credentials are what is needed to authorize the application
auth = twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
twitter_api = twitter.Twitter(auth=auth)

print twitter_api





#%% Example 3. Discovering the trending topics
import json
import twitter

def twitter_trends(twitter_api, woe_id):
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
    return twitter_api.trends.place(_id=woe_id)

# Sample usage

twitter_api = oauth_login()

# See https://dev.twitter.com/docs/api/1.1/get/trends/place and
# http://developer.yahoo.com/geo/geoplanet/ for details on
# Yahoo! Where On Earth ID

WORLD_WOE_ID = 1
world_trends = twitter_trends(twitter_api, WORLD_WOE_ID)
print json.dumps(world_trends, indent=1)

US_WOE_ID = 23424977
us_trends = twitter_trends(twitter_api, US_WOE_ID)
print json.dumps(us_trends, indent=1)




#%% Example 4. 
def twitter_search(twitter_api, q, max_results=200, **kw):

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets and 
    # https://dev.twitter.com/docs/using-search for details on advanced 
    # search criteria that may be useful for keyword arguments
    
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets    
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)
    
    statuses = search_results['statuses']
    
    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.
    
    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        
        if len(statuses) > max_results: 
            break
            
    return statuses

# Sample usage

twitter_api = oauth_login()

q = "NBA"
results = twitter_search(twitter_api, q, max_results=10)
        
# Show one sample search result by slicing the list...
print json.dumps(results[0], indent=1)


#%% Example 5. Constructing convenient function calls
from functools import partial

pp = partial(json.dumps, indent=1)

twitter_world_trends = partial(twitter_trends, twitter_api, WORLD_WOE_ID)

print pp(twitter_world_trends())

authenticated_twitter_search = partial(twitter_search, twitter_api)
results = authenticated_twitter_search("iPhone")
print pp(results)

authenticated_iphone_twitter_search = partial(authenticated_twitter_search, "iPhone")
results = authenticated_iphone_twitter_search()
print pp(results)





#%% Example 6. Saving and restoring JSON data with flat-text files
import io, json

def save_json(filename, data):
    with io.open('resources/ch09-twittercookbook/{0}.json'.format(filename), 
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def load_json(filename):
    with io.open('resources/ch09-twittercookbook/{0}.json'.format(filename), 
                 encoding='utf-8') as f:
        return f.read()

# Sample usage

q = 'CrossFit'

twitter_api = oauth_login()
results = twitter_search(twitter_api, q, max_results=10)

save_json(q, results)
results = load_json(q)

print json.dumps(results, indent=1)




#%% Example 7. 

#%% Example 8. Sampling the Twitter firehose with the Streaming API
# this didn't work
# can sample 1% at a time
# Finding topics of interest by using the filtering capablities it offers.

import twitter

# Query terms

q = 'Justin Bieber' # Comma-separated list of terms

print >> sys.stderr, 'Filtering the public timeline for track="%s"' % (q,)

# Returns an instance of twitter.Twitter
twitter_api = oauth_login()

# Reference the self.auth parameter
twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)

# See https://dev.twitter.com/docs/streaming-apis
stream = twitter_stream.statuses.filter(track=q)

# For illustrative purposes, when all else fails, search for Justin Bieber
# and something is sure to turn up (at least, on Twitter)

for tweet in stream:
    print tweet['text']
    # Save to a database in a particular collection






#%% Example 9. 

#%% Example 10. 

#%% Example 11. 

#%% Example 12. 

#%% Example 13. 

#%% Example 14. 

#%% Example 15. 

#%% Example 16. 

#%% Example 17. 

#%% Example 18. 

#%% Example 19. 

#%% Example 20. 

#%% Example 21. 

#%% Example 22. 

#%% Example 23. 

#%% Example 24. 

#%% Example 25. 

