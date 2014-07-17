# -*- coding: utf-8 -*-
"""
Created on Wed May 28 08:49:45 2014

@author: VAUGA026
"""
#%%
import twitter
import json

CONSUMER_KEY = '3dJxJpgFlvfdAcaj3IAJLzwR0'
CONSUMER_SECRET = 'eJTVOU98L5qYmz4m9pnLZFCjAROnJHRBQxxhQ4h22smNySOtDw'
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)
                           
twitter_api = twitter.Twitter(auth=auth)


WORLD_WOE_ID = 1
US_WOE_ID = 23424977

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
us_trends = twitter_api.trends.place(_id=US_WOE_ID)

print world_trends
print us_trends

#%%

print json.dumps(world_trends, indent=1)
world_trends_set = set([trend['name']
    for trend in world_trends[0]['trends']])
us_trends_set = set([trend['name']
    for trend in us_trends[0]['trends']])
common_trends = world_trends_set.intersection(us_trends_set)
print common_trends

#%%
q = '#Maleficent'
count = 100

search_results = twitter_api.search.tweets(q=q,count=count)
statuses = search_results['statuses']

for _ in range(5):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e:
        break
    
    kwargs = dict([kv.split('=') for kv in next_results[1:].split("&") ])
    
    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

print json.dumps(statuses[0],indent=1)

#%%
status_texts = [ status['text']
    for status in statuses ]
screen_names = [ user_mention['screen_name']
    for status in statuses 
        for user_mention in status['entities']['user_mentions']]
hashtags = [ hashtag['text']
    for status in statuses
        for hashtag in status['entities']['hashtags'] ]
words = [ w
    for t in status_texts
        for w in t.split() ]
            

print json.dumps(status_texts[0:5], indent=1)
print json.dumps(screen_names[0:5], indent=1)
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(words[0:5], indent=1)

#%%
from collections import Counter

for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print c.most_common()[:10]
    print
    
from prettytable import PrettyTable

for label, data in (('Word', words),
                    ('Screen Name', screen_names),
                    ('Hashtag',hashtags)):
    pt = PrettyTable(field_names=[label, 'Count'])
    c = Counter(data)
    [ pt.add_row(kv) for kv in c.most_common()[:10] ]
    pt.align[label], pt.align['Count'] = 'l', 'r'
    print pt
    
#%% page
def lexical_diversity(tokens):
    return 1.0*len(set(tokens))/len(tokens)

def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ])
    return 1.0*total_words/len(statuses)
    
print lexical_diversity(words)
print lexical_diversity(screen_names)
print lexical_diversity(hashtags)
print average_words(status_texts)

#%% page 35; retweets
retweets = [(status['retweet_count'],
             status['retweeted_status']['user']['screen_name'],
             status['text'])
             for status in statuses
                 if status.has_key('retweeted_status')
            ]
        
pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text'])
[ pt.add_row(row) for row in sorted(retweets, reverse=True)[:15] ]
pt.max_width['Text'] = 50
pt.align= 'l'
print pt

#%% page 38; plot
word_counts = sorted(Counter(words).values(),reverse=True)
plt.loglog(word_counts)
plt.ylabel="Freq"
plt.xlabel="Word Rank"

#%% page 41; histogram
for label, data in (('Words', words),
                    ('Screen Names', screen_names),
                    ('Hashtags', hashtags)):
    c = Counter(data)
    plt.hist(c.values())
    
    plt.title(label)
    plt.ylabel("Number of items in bin")
    plt.xlabel("Bins (Number of times an item appeared)")
    
    plt.figure()

counts = [count for count, _, _ in retweets]

plt.hist(counts)
plt.title("Retweets")
plt.xlabel("Bins (Number of times Retweeted)")
plt.ylabel("Number of tweets in bin")
#%%
