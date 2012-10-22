# -*- coding: UTF-8 -*-
from time import time, sleep
import urllib2
import json


start = time()
begin = time()
sum_sol_time=0
sum_request_time = 0
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
  qlist = query.split(' ')
  stride = create_stride(len(qlist))
  dp_table = {"query": query, 'solution': None} 
  r = gen(stride-1,0,len(qlist),qlist,dp_table)
  print "Total Elapsed: " + str(time() - begin)  
  print "Total spent on solutions: " + str(sum_sol_time)
  print "Total spent on requests: " + str(sum_request_time)
  return r
  
  
def create_stride(n):
  # A simple heuristic based on the length of the input and
  # the average length of songs on Spotify.
  if n > 10:
    return 5
  elif n > 6:
    return 4
  else:
    return min(3,n)
    
def gen(r,c,n,l,dp_table):
  global sum_sol_time
  start_c = c
  for i in range(r,-1,-1):
    for j in range(c,n-i):
      substring = ' '.join(l[j:j+i+1])
      #print "attempting to match: " + substring
      if (i,j) not in dp_table:
        #print substring + " is not in the dp table!"
        m = match(substring)
        if m["title"] is None:
          #print substring + " has no exact matches."
          dp_table[(i,j)] = None       
          if m["total_results"] == 0:
            #print substring + " has no partial matches either!"
             #Fill in zeroes for entries below in the same column (j)
             #and lower diagonal entries
            for idx in range(0,n-i-1):
              dp_table[(idx+i,j)] = None
              dp_table[(idx+i,j-idx-1)] = None
        else:
          print substring + " has some partial match!"
          dp_table[(i,j)] = m  
      #else:
        #print substring +"  is in the dp_table and has value " + str(dp_table[(i,j)]) 
      r = dp_table[(i,j)] 
      if r is not None:
        #print "Partial match exits for: " + r["title"]
        #print (i,j,n,start_c)
        if j != start_c:
          #print "Recursing on front:  " + str((j-1,start_c,j))
          gen(j-1,start_c,j,l,dp_table)
          #print "Recursion complete for some front"
        if j+i+1 != n:
          #print "Recursing on back:  " + str((n-i-j-1,i+j+1,n))
          gen(n-i-j-1,i+j+1,n,l,dp_table)
          #print "Recursion complete for some back"
        #print dp_table
        if dp_table['solution'] == None:
          matches = []
          for k,v in dp_table.iteritems():
            if v is not None and k != 'query' and k != 'solution':
              matches.append(v)
              t= time()
              sol = get_solution(matches,dp_table['query'].lower())
              e= time()-t
              sum_sol_time += e
              #print "calculating sol took " + str(e) + "seconds"
              #print sol
              if sol != [False]:
                dp_table['solution'] = sol
                return sol
        else:
          return dp_table['solution']
  return [None]
  
  
def get_solution(matches,query):
  #print 'getting solution'
  if query == '':
    #print "query is empty!"
    return []
  elif matches == [] or matches is None:
    #print 'matches is empty or None'
    return [False]
  else:
    pos_solutions = []
    #print "Query is currently: " + query
    for match in matches:
      #print match
      if query.find(match['title'].lower()) == 0:
        rem_matches = matches[:]
        rem_matches.remove(match)
        part_sol = get_solution(rem_matches,query.replace(match['title'].lower(),'',1).strip())
        #print part_sol
        sol= [[match['title'].encode('utf-8'), match['artist'].encode('utf-8'), match['link'].encode('utf-8') ]]+part_sol
        if all(elt is not False for elt in sol):
          return sol
    return [False]


def match(substring):
  search_results = query_api(substring)
  total_results = search_results['info']['num_results']
  for track in search_results["tracks"]:
    if track["name"].lower() == substring.lower():
      title = track["name"]
      artist = track["artists"][0]["name"]
      link = track["href"].split(':')[-1]
      return {"title": title, "artist": artist, "link": link, "total_results": total_results }
  return {"title": None, "total_results": total_results }
  
def query_api(query):
  global start
  global num_requests
  global cache
  global sum_request_time
  search_query = urllib2.quote(query)
  #print "Searching for " + query + " as " + search_query + " on the Metadata API"
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
    t=time()
    data = urllib2.urlopen(metadata_url+search_query)
    result = data.read()
    num_requests += 1
    e=time()-t
    #print "request took " + str(e) + " seconds"
    sum_request_time += e
  except Exception, e:
    print str(e)
  return json.loads(result)