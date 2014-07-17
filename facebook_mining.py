# -*- coding: utf-8 -*-
"""
Created on Wed May 28 11:08:13 2014

@author: VAUGA026
"""

#%% page 53
import requests
import json

base_url = 'https://graph.facebook.com/alankvaughn'

fields = 'id,name,friends.limit(10).fields(likes.limit(10))'
ACCESS_TOKEN = 'CAACEdEose0cBAHHZCBg2s9hIDDGG6IVGTnrPtrNbLHXK96GiYROJ54GZBTr6OX2n6CfQkKm1s432fKb8clqlbsvOlp8XyPCS2q3NydTNRvKehi70G6ZAQrEIWmzTBiK7YLN0O0qcWQow22Dd8uBi8D81fWjzsdS4tfTE86ALkM3KuYzFqiMWavsq52FCzqXiUQV5WXp6gZDZD'

url = '%s?fields=%s&access_token=%s' % \
    (base_url, fields, ACCESS_TOKEN,)
content = requests.get(url).json()

print json.dumps(content, indent=1)


#%%
get_object(self, id, **args)
get_obj


#%%
pp(g.request('search', {'q' : 'pepsi', 'type' : 'page', 'limit' : 5}))
pp(g.request('search', {'q' : 'coke', 'type' : 'page', 'limit' : 5}))

pepsi_id = '56381779049'
pepsi_id = '40796308305'

def int_format(n): return "{:,}".format(n)

print "Pepsi likes:",int_format(g.get_object(pepsi_id)['likes'])
print "Coke likes:",int_format(g.get_object(coke_id)['likes'])

