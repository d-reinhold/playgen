# -*- coding: UTF-8 -*-
from time import time, sleep
import json
import urllib2
import urllib3
from pprint import pprint
import re

class PlaylistGenerator:
  
  
  def __init__(self, query):
    """This method initializes a playlist generator for a single query"""
    self.query = query
    self.begin = time()
    self.timeout = 25  # This is so we don't go over the 30 second limit!
    self.http = urllib3.PoolManager()    
    self.potential_solutions = []
    self.best_solution = None
    self.solution_is_final = False
    self.dp_table = {} 
    

  def get_playlist(self):
    """This method gets the best playlist it can find for a query.
       If a perfect solution (i.e. a playlist where all the words
       from the query appear) has been found, return that, otherwise
       return the next best thing!"""
    qlist = self.query.split(' ')
    stride = self.create_stride(len(qlist))
    result=self.fill_table(stride-1,0,len(qlist),qlist)
    print "Total Elapsed: " + str(time() - self.begin)  
    if self.solution_is_final:
      return ['perfect',self.best_solution]
    else:
      return ['best',self.get_best_solution()]
    
    
  def create_stride(self,n):
    """ A simple heuristic based on the length of the input and
        the average length of songs on Spotify. This gives us a
        stride pattern that vastly increases the speed of playlist
        generation."""
    if n > 10:
      return 5
    elif n > 6:
      return 4
    else:
      return min(3,n)
    
    
  def fill_table(self,r,c,n,l):
    """ fill_table is a modified dynamic programming algorithm that 
        succeeds in two big ways: first it caches the results of API
        lookups so we don't have to query for the same thing multiple
        times, and it also finds good solutions quickly by filling in the 
        DP table in an intellegent order. Please ask me questions if any
        of this isn't totally clear!"""
    curr_dict_len = len(self.dp_table)
    start_c = c
    for i in range(r,-1,-1):
      for j in range(c,n-i):
        if time() - self.begin > self.timeout:
          return self.best_solution
        substring = ' '.join(l[j:j+i+1])
        if (i,j) not in self.dp_table:
          m = self.match(substring)
          if m["title"] is None:
            self.dp_table[(i,j)] = None       
            if m["total_results"] == 0:
               #Fill in zeroes for entries below in the same column (j)
               #and lower diagonal entries
              for idx in range(0,n-i-1):
                self.dp_table[(idx+i,j)] = None
                self.dp_table[(idx+i,j-idx-1)] = None
          else:
            self.dp_table[(i,j)] = m  
        r = self.dp_table[(i,j)] 
        if r is not None:
          if j != start_c:
            self.fill_table(j-1,start_c,j,l)
          if j+i+1 != n:
            self.fill_table(n-i-j-1,i+j+1,n,l)
            # before updating partial solutions, make sure stuff has been added to
            # the DP table, otherwise there's no point!
          if self.solution_is_final == False and curr_dict_len < len(self.dp_table):          
            return self.check_for_solutions()
          else:
            return self.best_solution
          

  def check_for_solutions(self):    
    """ This method sets up the data structures for the partial_solutions
        method. This code is messy and somewhat nonsensical; but hopefully
        sufficient for a 3 day hack!"""   
    matches = []
    substrings = []
    for k,v in self.dp_table.iteritems():
      if v is not None:
        matches.append(v)
        substrings.append([v])
    if self.potential_solutions == []:
      psols = self.partial_solutions(self.query,matches,substrings)
      
    else:
      psols = self.partial_solutions(self.query,matches,self.potential_solutions)
    self.potential_solutions = remove_dupes(psols)
    for psol in psols:
      is_best = " ".join(map((lambda x: x['title']),psol)).lower()
      if is_best == self.query.lower():
        self.best_solution = psol
        self.solution_is_final = True
        return psol
  
      
  def partial_solutions(self,query,matches,potential_sols):
    """ Partial solutions is a rather silly method that periodically updates
        the generator's current list of possible solutions. I make no claims
        of optimality here, but it does do the trick! If I had more time, I 
        would definitely improve this method! """
    # matches is a list of dicts
    # potential_sols is a list lists of dicts
    partial_sols = []
    for potential_sol in potential_sols:
      sstring = ".*".join(map((lambda x: x['title']),potential_sol)).lower()
      if re.search(sstring,query.lower()) is not None:
        if time() - self.begin > self.timeout:
          return [potential_sol]
        partial_sols.append(potential_sol)
        new_potential_solutions = []
        for m in matches:
          nps = potential_sol[:]
          nps.append(m)
          new_potential_solutions.append(nps)
        psol = self.partial_solutions(query,matches,new_potential_solutions)
        partial_sols=partial_sols+psol
    return partial_sols



  def get_best_solution(self):
    """ This method finds the best playlist from a list of possible 
        playlists. It first compiles a list of playlists which contain
        are of a maximal length. It then selects the best of these by selecting 
        the one with the most tracks in it. """
    print "getting best solution"
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
    least_number_of_tracks = 999999
    for bsol in prelim_best_solutions:
      if len(bsol) < least_number_of_tracks:
         least_number_of_tracks = len(bsol)
         best_solution = bsol
    return best_solution     


  def match(self,substring):
    """ Match takes a substring and looks it up on the Spotify Metadata API
        It then parses the results and tries to find tracks that match the 
        query exactly. This process would be a lot more efficient if the API 
        supported exact matches as a search feature! """
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
    """ This method queries the Spotify Metadata API to find all tracks that contain
        the substring 'query' """
    search_query = urllib2.quote(query)
    metadata_url = "http://ws.spotify.com/search/1/track.json?q=track:"
    try:
      result = self.http.request('GET', metadata_url+search_query).data
    except Exception, e:
      print str(e)
    return json.loads(result)
    
    
def remove_dupes(seq): 
  """ A simple method to remove duplicates from a list of non hashable objects"""
  noDupes = []
  [noDupes.append(i) for i in seq if not noDupes.count(i)]
  return noDupes