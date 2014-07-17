# -*- coding: utf-8 -*-
"""
Created on Wed May 28 13:32:45 2014

@author: VAUGA026
"""
#%% page 92; authorization
from linkedin import linkedin

CONSUMER_KEY = '75xna7vqp4th60'
CONSUMER_SECRET = 'ODLDYhEoNzSi4G56'
USER_TOKEN = '24118801-6c47-4c39-9eb7-6a5e408845a7'
USER_SECRET = '67d2a2d5-61c4-4f88-8497-d4cae9d68521'

RETURN_URL = ''

auth = linkedin.LinkedInDeveloperAuthentication(CONSUMER_KEY, CONSUMER_SECRET,
                                                USER_TOKEN, USER_SECRET,
                                                RETURN_URL,
                                                permissions=linkedin.PERMISSIONS.enums.values())

app = linkedin.LinkedInApplication(auth)

app.get_profile()

#%% 93
import json

connections = app.get_connections()
connections_data = 'resources/ch03-linkedin/linkedin_connections.json'

f = open(connections_data, 'w')
f.write(json.dumps(connections, indent=1))
f.close()

from prettytable import PrettyTable

pt = PrettyTable(field_names=['Name', 'Location'])
pt.align = 'l'

[ pt.add_row((c['firstName'] + ' ' + c['lastName'], c['location']['name']))
    for c in connections['values']
        if c.has_key('location')]

print pt

#%%
my_positions = app.get_profile(selectors=['positions'])
print json.dumps(my_positions, indent=1)

connection_id = connections['values'][0]['id']
connection_positions = app.get_profile(member_id = connection_id,
                                       selectors=['positions'])
print json.dumps(connection_positions, indent=1)

my_positions = app.get_profile(selectors=['positions:(company:(name,industry,id))'])
print json.dumps(my_positions, indent=1)

#%% page 101

import os
import csv
from collections import Counter
from operator import itemgetter
from prettytable import PrettyTable

CSV_FILE = os.path.join('C:\\Users\\vauga026\\Documents\\Python Scripts\\linkedin_connections_export_microsoft_outlook.csv')


transforms = [(', Inc.', ''), (',Inc', ''), (', LLC', ''), (', LLP', ''),
              (' LLC', ''), (' Inc.', ''), (' Inc', '')]

csvReader = csv.DictReader(open(CSV_FILE), delimiter=',', quotechar='"')
contacts = [row for row in csvReader]
companies = [c['Company'].strip() for c in contacts if c['Company'].strip() != '']

#%% page 102
for i, _ in enumerate(companies):
    for transform in transforms:
        companies[i] = companies[i].replace(*transform)

pt = PrettyTable(field_names=['Company', 'Freq'])
pt.align = 'l'
c = Counter(companies)
[pt.add_row([company, freq])
    for (company, freq) in sorted(c.items(), key=itemgetter(1), reverse=True)
        if freq > 1]
print pt

#%% page 104
transforms = [
('Sr.', 'Senior'),
('Sr', 'Senior'),
('Jr.', 'Junior'),
('Jr', 'Junior'),
('CEO', 'Chief Executive Officer'),
('VP', 'Vice President')]

titles = []
for contact in contacts:
    titles.extend([t.strip() for t in contact['Job Title'].split('/')
        if contact['Job Title'].strip() != ''])

for i, _ in enumerate(titles):
    for transform in transforms:
        titles[i] = titles[i].replace(*transform)

pt = PrettyTable(field_names=['Title', 'Freq'])
pt.align = 'l'
c = Counter(titles)
[pt.add_row([title, freq])
 for (title, freq) in sorted(c.items(), key=itemgetter(1), reverse=True)
            if freq > 1]
print pt

#%% page 105
tokens = []
for title in titles:
    tokens.extend([t.strip(',') for t in title.split()])
pt = PrettyTable(field_names=['Token', 'Freq'])
pt.aling = 'l'
c = Counter(tokens)
[pt.add_row([token, freq])
 for (token, freq) in sorted(c.items(), key=itemgetter(1), reverse=True)
     if freq >1 and len(token) > 2 ]

print pt

#%%
from geopy import geocoders

GEO_APP_KEY = 'AotKDSYPHl8R9Pu8yQMwJi-urxZi5XgnFhrnF4SKt-yM6UU-en8DBajt5vw8EEBX'
g = geocoders.Bing(GEO_APP_KEY)

transforms = [('Greater ', ''), (' Area', '')]

results = {}
for c in connections['values']:
    if not c.has_key('location'): continue
        
    transformed_location = c['location']['name']
    for transform in transforms:
        transformed_location = transformed_location.replace(*transform)
    geo = g.geocode(transformed_location, exactly_one=False)
    if geo == []: continue
    results.update({ c['location']['name'] : geo })

print json.dumps(results, indent=1)

#%%
import re

pattern = re.compile('.*([A-Z]{2}).*')
def parseStateFromBingResult(r):
    result = pattern.search(r[0][0])
    if result == None:
        print "Unresolved match:", r
        return "???"
    elif len(result.groups()) == 1:
        print result.groups()
        return result.groups()[0]
    else:
        print "Unresolved match:", result.groups()
        return "???"

transforms = [('Greater ', ''), (' Area', '')]

results = {}
for c in connections['values']:
    if not c.has_key('location'): continue
    if not c['location']['country']['code'] == 'us': continue
    
    transformed_location = c['location']['name']
    for transform in transforms:
        transformed_location = transformed_location.replace(*transform)
    
    geo = g.geocode(transformed_location, exactly_one=False)
    if geo == []: continue
    parsed_state = parseStateFromBingResult(geo)
    if parsed_state !="???":
        results.update({c['location']['name'] : parsed_state})

print json.dumps(results, indent=1)

#%% page 113
import nltk as nltk
ceo_bigrams = nltk.bigrams("Chief Executive Officer".split(), pad_right=True,
                           pad_left=True)

#%% page 115
from nltk.metrics.distance import jaccard_distance

DISTANCE_THRESHOLD = 0.5
DISTANCE = jaccard_distance

def cluster_contacts_by_title(csv_file):
    transforms = [
    ('Sr.', 'Senior'),
    ('Sr', 'Senior'),
    ('Jr.', 'Junior'),
    ('Jr', 'Junior'),
    ('CEO', 'Chief Executive Officer'),
    ('VP', 'Vice President')]
    separators = ['/', 'and', '&']
    csvReader = csv.DictReader(open(csv_file), delimiter=',', quotechar='"')
    contacts = [row for row in csvReader]
    all_titles = []
    for i, _ in enumerate(contacts):
        if contacts[i]['Job Title'] == '':
            contacts[i]['Job Title'] = ['']
            continue
        titles = [contacts[i]['Job Title']]
        for title in titles:
            for separator in separators:
                if title.find(separator) >= 0:
                    titles.remove(title)
                    titles.extend([title.strip() for title in title.split(separator)
                        if title.strip() != ''])
        
        for transform in transforms:
            titles = [title.replace(*transform) for title in titles]
        contacts[i]['Job Titles'] = titles
        all_titles.extend(titles)    
        
    all_titles = list(set(all_titles))
    clusters = {}
    for title1 in all_titles:
        clusters[title1] = []
        for title2 in all_titles:
            if title2 in clusters[title1] or clusters.has_key(title2) and title1 \
                in clusters[title2]:
                continue
            distance = DISTANCE(set(title1.split()), set(title2.split()))        
            if distance < DISTANCE_THRESHOLD:
                clusters[title1].append(title2)
    clusters = [clusters[title] for title in clusters if len(clusters[title]) > 1]
    clustered_contacts = {}
    for cluster in clusters:
        clustered_contacts[tuple(cluster)] = []
        for contact in contacts:
            for title in contact['Job Titles']:
                if title in cluster:
                    clustered_contacts[tuple(cluster)].append('%s %s'
                        % (contact['First Name'], contact['Last Name']))
    return clustered_contacts

clustered_contacts = cluster_contacts_by_title(CSV_FILE)

print clustered_contacts
for titles in clustered_contacts:
    common_titles_heading = 'Common Titles: ' + ', '.join(titles)
    
    descriptive_terms = set(titles[0].split())
    for title in titles:
        descriptive_terms.intersection_update(set(title.split()))
    descriptive_terms_heading = 'Descriptive Terms: ' \
        + ', ',.join(descriptive_terms)
    print descriptive_terms_heading
    print '-' * max(len(descriptive_terms_heading), len(common_titles_heading))
    print '\n'.join(clustered_contacts[titles])
    print
    