import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from pprint import pprint
from generate_playlist import PlaylistGenerator

app = Flask(__name__)
app.secret_key = 'nw485qyow745ynd378y'

@app.route('/')
def home():
    return render_template('home.html')
  
@app.route('/create_playlist', methods=['POST'])
def create_playlist():
  q = request.form['query']
  r = PlaylistGenerator(q).get_playlist()
  if r[1] is None:
    return render_template('no_playlist.html', query=q)
  else:
    return render_template('playlist.html', playlist = r)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
    


  

  