# -*- coding: UTF-8 -*-
from time import time, sleep
import urllib2
import json


start = time()
begin = time()
num_requests = 0
cache = {}

def playlist(query):
  global start
  global begin
  global num_requests
  start = time()
  begin = time()
  num_requests = 0
  # search for individual words first to ensure a solution exists
  r = gen(query)
  print "Total Elapsed: " + str(time() - begin)   
  return r
  
  
  

# return a list of track ids
def gen(query):
  if query == '':
    print "query was empty string"
    return []
  l = query.split(' ')
  matches = [] # make a priority queue?
  for i in range(len(l),0,-1):
    for j in range(0,len(l)-i+1):
      substring = ' '.join(l[j:j+i])
      print "attempting to match: " + substring
      r = match(substring)
      if r is not None:
        print "Found a partial match: " + r["title"]
        back = []
        front = []
        if j != 0:
          # need to check the front substring
          front = gen(' '.join(l[0:j]))
          print front
        if j+i != len(l):
          # need to check the back substring
          back = gen(' '.join(l[j+i:len(l)+1]))
          print back
        uids = front+[r["title"],r["artist"]]+back
        if all(elt is not None for elt in uids):
          #matches.append(uids)
          return uids
        else:
          print "found some Nones!"
  return [None]
       
  
def match(substring):
  # first check the cache for a possible match!
  if substring in cache:
    print "Found " + substring + " in the cache!"
    return {"title": cache[substring], "artist": cache[substring]["artist"], "uid": cache[substring]["uid"]}
  else:
    search_results = query_api(substring)
    total_matches = search_results['info']['num_results']
    print total_matches
    for track in search_results["tracks"]:
      #if "external-ids" in track:
        #cache[track["name"]] = {"title": track["name"], "artist": track["artists"][0]["name"], "uid": track["external-ids"][0]["id"]}
      #print q.lower()
      #print track["name"].encode('utf8').lower()
      if track["name"].lower() == substring.lower():
        title = track["name"]
        artist = track["artists"][0]["name"]
        uid = track["external-ids"][0]["id"]
        return {"title": title, "artist": artist, "uid": uid}
    return None
  
def query_api(query):
  global start
  global num_requests
  global cache
  search_query = urllib2.quote(query)
  print "Searching for " + query + " as " + search_query + " on the Metadata API"
  metadata_url = "http://ws.spotify.com/search/1/track.json?q=track:"
  elapsed = time()-start;
  if num_requests == 10:
    num_requests = 0
    if elapsed < 1:
      print str(elapsed)
      print "Sleeping!"
      sleep(1 - elapsed)
      start = time()
  try:
    data = urllib2.urlopen(metadata_url+search_query)
    result = data.read()
    num_requests += 1
  except Exception, e:
    return str(e)
  return json.loads(result)
  
  
'''
    def gen(q):
      begin = time()
      print "Generating Playlist"
      query_list = q.split(' ')
      results = {}
      num_requests = 0
      start = time()
      for i in range(len(query_list)):
        for j in range(i+1,len(query_list)+1):
          search_string = " ".join(query_list[i:j])
          search_query = urllib2.quote(search_string)
          print "Searching for " + search_string + " as " + search_query
          metadata_url = "http://ws.spotify.com/search/1/track.json?q="
          elapsed = time()-start;
          if num_requests == 10 and elapsed < 1:
            print str(elapsed)
            print "Sleeping!"
            sleep(1 - elapsed)
            num_requests = 0
            start = time()
          try:
            data = urllib2.urlopen(metadata_url+search_query)
            result = data.read()
            num_requests += 1
          except Exception, e:
            return str(e)
          search_results = json.loads(result)
          total_matches = search_results['info']['num_results']
          perfect_matches = 0

          title = "No Matches"
          artist = "None"
          uid = "NA"
          for track in search_results["tracks"]:
            #print q.lower()
            #print track["name"].encode('utf8').lower()
            if track["name"].lower() == q.lower():
              if title == "No Matches":
                title = track["name"]
                artist = track["artists"][0]["name"]
                uid = track["external-ids"][0]["id"]
              perfect_matches += 1
              break


          print "Num results: " + str(total_matches)
          print "Perfect Matches: " + str(perfect_matches)
          print "Track: " + title
          print "Artist: "  + artist

          results[search_string] = {"total_matches": total_matches, \
                                   "perfect_matches": perfect_matches, \
                                   "best": { \
                                           "title" : title, \
                                           "artist": artist, \
                                           "uid"    : uid \
                                           } \
                                  }
      print "Total Elapsed: " + str(time() - begin)            
      return results
      '''