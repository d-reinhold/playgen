# -*- coding: UTF-8 -*-
from time import time, sleep
import json
import urllib3
from pprint import pprint
import re
from unicodedata import category


class PlaylistGenerator:
  
  def __init__(self, query):
    """This method initializes a playlist generator for a single query"""
    self.query = query
    self.begin = time()
    self.start = time()
    self.request_queue = {}
    self.http = urllib3.PoolManager()
    self.sum_sol_time=0
    self.sum_request_time = 0
    self.num_requests = 0
    self.potential_solutions = []
    self.best_solution = None
    self.solution_is_final = False
    self.dp_table = {} 
    

  def get_playlist(self):
    qlist = self.query.split(' ')
    stride = self.create_stride(len(qlist))
    result=self.fill_table(stride-1,0,len(qlist),qlist)

    print "Here are the partial solutions:"
    pprint(self.potential_solutions)
    print "Total Elapsed: " + str(time() - self.begin)  
    print "Total spent on solutions: " + str(self.sum_sol_time)
    print "Total spent on requests: " + str(self.sum_request_time)
    if self.solution_is_final:
      return ['perfect',self.best_solution]
    else:
      return ['best',self.get_best_solution()]
    

  def create_stride(self,n):
    # A simple heuristic based on the length of the input and
    # the average length of songs on Spotify.
    if n > 10:
      return 5
    elif n > 6:
      return 4
    else:
      return min(3,n)
    
  def fill_table(self,r,c,n,l):
    curr_dict_len = len(self.dp_table)
    start_c = c
    for i in range(r,-1,-1):
      for j in range(c,n-i):
        substring = ' '.join(l[j:j+i+1])
        print "attempting to match: " + substring
        if (i,j) not in self.dp_table:
          #print substring + " is not in the dp table!"
          m = self.match(substring)
          if m["title"] is None:
            #print substring + " has no exact matches."
            self.dp_table[(i,j)] = None       
            if m["total_results"] == 0:
              #print substring + " has no partial matches either!"
               #Fill in zeroes for entries below in the same column (j)
               #and lower diagonal entries
              for idx in range(0,n-i-1):
                self.dp_table[(idx+i,j)] = None
                self.dp_table[(idx+i,j-idx-1)] = None
          else:
            print substring + " has some partial match!"
            self.dp_table[(i,j)] = m  
        #else:
          #print substring +"  is in the dp_table and has value " + str(dp_table[(i,j)]) 
        r = self.dp_table[(i,j)] 
        if r is not None:
          #print "Partial match exits for: " + r["title"]
          #print (i,j,n,start_c)
          if j != start_c:
            print "Recursing on front:  " + str((j-1,start_c,j))
            self.fill_table(j-1,start_c,j,l)
            print "Recursion complete for some front"
          if j+i+1 != n:
            print "Recursing on back:  " + str((n-i-j-1,i+j+1,n))
            self.fill_table(n-i-j-1,i+j+1,n,l)
            print "Recursion complete for some back"
          #print dp_table

          if self.solution_is_final == False and curr_dict_len < len(self.dp_table):
            matches = []
            substrings = []
            for k,v in self.dp_table.iteritems():
              if v is not None:
                matches.append(v)
                substrings.append([v])
            t= time()
            #sol = self.get_solution(matches,self.query.lower())
            if self.potential_solutions == []:
              psols = self.partial_solutions(self.query,matches,substrings)
            else:
              psols = self.partial_solutions(self.query,matches,self.potential_solutions)
            e= time()-t
            self.sum_sol_time += e
            self.potential_solutions = f4(psols)
            #print "calculating sol took " + str(e) + "seconds"
            #print sol
            for psol in psols:
              is_best = " ".join(map((lambda x: x['title']),psol)).lower()
              print "Checking if: " + is_best+ " is a final answer"
              if is_best == self.query.lower():
                self.best_solution = psol
                self.solution_is_final = True
                return psol
          else:
            return self.best_solution
  
  

      
  def partial_solutions(self,query,matches,potential_sols):
    print "starting psols!"
    # matches is a list of dicts
    # substrings is a list lists of dicts
    #print "Substrings! " + str(substrings)
    partial_sols = []
    for potential_sol in potential_sols:
      print str(potential_sol) + " is a potential solution list"
      sstring = ".*".join(map((lambda x: x['title']),potential_sol)).lower()
      print "checking " + sstring
      if re.search(sstring,query.lower()) is not None:
        print sstring + " is a possible solution!"
        partial_sols.append(potential_sol)
        new_potential_solutions = []
        for m in matches:
          nps = potential_sol[:]
          nps.append(m)
          new_potential_solutions.append(nps)
        psol = self.partial_solutions(query,matches,new_potential_solutions)
        #pprint(psol)
        partial_sols=partial_sols+psol
    return partial_sols

  def get_best_solution(self):
    greatest_number_of_words = 0
    prelim_best_solutions = []
    for psol in self.potential_solutions:
      l = len(" ".join(map(lambda x:x['title'],psol)))
      if l == greatest_number_of_words:
        prelim_best_solutions.append(psol)
      elif l > greatest_number_of_words:
        greatest_number_of_words = l
        prelim_best_solutions = [psol]
    best_solution = None
    greatest_number_of_titles = 0
    for bsol in prelim_best_solutions:
      if len(bsol) > greatest_number_of_titles:
         greatest_number_of_titles = len(bsol)
         best_solution = bsol
    return best_solution     


  def match(self,substring):
    search_results = self.query_api(substring)
    total_results = search_results['info']['num_results']
    for track in search_results["tracks"]:
      if track["name"].lower() == substring.lower():
        title = track["name"]
        artist = track["artists"][0]["name"]
        link = track["href"].split(':')[-1]
        return {"title": title, "artist": artist, "link": link, "total_results": total_results }
    return {"title": None, "total_results": total_results }
  
  def query_api(self,query):
    search_query = urllib2.quote(query)
    #print "Searching for " + query + " as " + search_query + " on the Metadata API"
    metadata_url = "http://ws.spotify.com/search/1/track.json?q=track:"
    elapsed = time()-self.start;
    if self.num_requests == 10:
      self.num_requests = 0
      if elapsed < 1:
        print str(elapsed)
        print "Sleeping!"
        sleep(1 - elapsed)
        self.start = time()
    try:
      result = self.http.request('GET', metadata_url+search_query).data
      self.num_requests += 1
    except Exception, e:
      print str(e)
    return json.loads(result)
    
def f4(seq): 
   # order preserving
   noDupes = []
   [noDupes.append(i) for i in seq if not noDupes.count(i)]
   return noDupes