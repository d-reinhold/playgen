import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from pprint import pprint
import generate_playlist

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/create_playlist', methods=['POST'])
def create_playlist():
  q = request.form['query']
  r = generate_playlist.gen(q)
  pprint(r)
  rstring = " ".join(r)
  flash('Submitted: ' + q + '. \n' + "Best Match: " + rstring)
  return render_template('home.html')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    


  

  