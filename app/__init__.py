# Squash (Jason Chan, Aoanul Hoque, Isabel Zheng, Maya Berchin)
# p01
# SoftDev
# 11/25/25--2025-12-22

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect, url_for
import urllib.request
import urllib.error
import json
import sqlite3
import data

# ----------------------------------SETUP---------------------------------- #

data.create_user_data()
DB_FILE="data.db"

app = Flask(__name__)
app.secret_key = "secret"

file_err = "file not found error"
url_err = "url error"

# ----------------------------------PAGES---------------------------------- #

@app.route("/", methods=['GET', 'POST'])
def index():
    # stored active session, take user to response page
    if 'username' in session:
        return redirect(url_for("home"))

    # no active session, user is taken to login
    return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # store username and password as a variable
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # render login page if username or password box is empty
        if not username or not password:
            return render_template('login.html', error="No username or password inputted")

        # check if password is correct, if not then reload page
        if not data.auth(username, password):
            return render_template("login.html", error="Username or password is incorrect")

        # if password is correct redirect home
        session["username"] = username
        return redirect(url_for("home"))

    return render_template('login.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('home.html', username=session['username'], points=data.get_score(session['username']))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # reload page if no username or password was entered
        if not username or not password:
            return render_template("register.html", error="No username or password inputted")

        # puts user into database unless if there's an error
        execute_register = data.register_user(username, password)
        if execute_register == "success":
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return render_template("register.html", error = execute_register)
    return render_template("register.html")

def get_trivia_question():

    # this api doesn't need a key
    url = f"https://opentdb.com/api.php?amount=1" # Endpoint URL
    data = get_data(url)

    return data   # Returning the python dictionary for route, or "url error" if not found

@app.route("/trivia")
def trivia():
    trivia_data = get_trivia_question()

    if (trivia_data == url_err):
        return render_template("keyerror.html", API="opentdb", err=trivia_data)

    return render_template("trivia.html", username=session['username'], trivia=trivia_data)

def get_joke():
    url = "https://v2.jokeapi.dev/joke/Programming?blacklistFlags=religious,political,racist,sexist"
    data = get_data (url)
    return data   
        
@app.route("/jokes") 
def jokes(): 
    joke_db = get_joke()
    if (joke_db == url_err):
        return render_template ("keyerror.html", API = "Jokes API", err = joke_data)
    return render_template("jokes.html", username = session['username'], joke = joke_db)

@app.route("/activites")
def activities():

    url = "https://bored-api.appbrewery.com/random"

    data = get_data(url)
    if (data == url_err):
        return render_template("keyerror.html", API="Bored API", err=data)

    return render_template("activities.html", username=session['username'], data=data)

@app.route("/logout")
def logout():
    session.pop('username', None) # remove username from session
    return redirect(url_for('login'))


# ----------------------------------HELPERS---------------------------------- #

# turns out none of our APIs need keys!
# not sure this works since I wasn't able to test it, but just in case we do need keys, here is my progress.
'''
# return the key in the specified file, or "file not found"
def get_key(filename):
    try:
        with open(filename) as f:
            key = f.read().strip() # we read the txt file that only contains the key and strip any newline characters.
            return key
    except FileNotFoundError:
        return file_err
'''

# return the data string from the api url, or "url error"
def get_data(url):
    try:
        response = urllib.request.urlopen(url) # This sends the HTTP GET request to Nasa API and urlopen returns a response obj.
        data = json.loads(response.read().decode()) # This decodes the response, which is in bytes, into string and then loads the json string into a python dictionary: data.
        return data
    except urllib.error.URLError:
        return url_err

# ----------------------------------MAIN---------------------------------- #

if __name__=='__main__':
    app.debug = True
    app.run()
