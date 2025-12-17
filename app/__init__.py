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
import time

OPENTDB_COOLDOWN = 5.1
_last_opentdb_call = 0.0

TRIVIA_POOL = {"easy": [], "medium": [], "hard": []}


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

def opentdb_get(url):
    global _last_opentdb_call
    now = time.monotonic()
    wait = OPENTDB_COOLDOWN - (now - _last_opentdb_call)
    if wait > 0:
        time.sleep(wait)
    _last_opentdb_call = time.monotonic()
    return get_data(url)


def refill_pool(difficulty, amount=10):
    url = f"https://opentdb.com/api.php?amount={amount}&difficulty={difficulty}"
    for _ in range(3):
        data = opentdb_get(url)
        if data == url_err:
            continue
        if data.get("response_code") == 5:
            time.sleep(OPENTDB_COOLDOWN)
            continue
        if data.get("response_code") == 0 and data.get("results"):
            TRIVIA_POOL[difficulty].extend(data["results"])
            return True
    return False


def get_trivia_question(difficulty=None):
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "easy"

    if not TRIVIA_POOL[difficulty]:
        ok = refill_pool(difficulty, amount=10)
        if not ok:
            return url_err

    q = TRIVIA_POOL[difficulty].pop(0)
    return {"response_code": 0, "results": [q]}

@app.route("/trivia", methods=["GET", "POST"])
def trivia():
    if request.method == "GET":
        return render_template("trivia.html", username=session["username"], stage="choose")

    chosen = request.form.get("difficulty") or request.form.get("current_difficulty")
    if chosen not in ["easy", "medium", "hard"]:
        chosen = "easy"

    trivia_data = get_trivia_question(chosen)

    if trivia_data == url_err:
        return render_template("keyerror.html", API="opentdb", err=trivia_data)

    return render_template(
        "trivia.html",
        username=session["username"],
        trivia=trivia_data,
        stage="question",
        chosen_difficulty=chosen
    )
def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
    data = get_data (url)
    return data

@app.route("/jokes")
def jokes():
    joke_db = get_joke()
    if (joke_db == url_err):
        return render_template ("keyerror.html", API = "Jokes API", err = joke_data)
    return render_template("jokes.html", username = session['username'], joke = joke_db)

@app.route("/activites", methods=["GET", "POST"])
def activities():

    url = "https://bored-api.appbrewery.com/random"

    data = get_data(url)
    if (data == url_err):
        return render_template("keyerror.html", API="Bored API", err=data)

    # get values for sliders. set to default
    num_val = 0
    price = 0
    accessibility = 0
    duration = 0
    slider_mode = 0
    if "slider_mode" in request.form:
        # all values in here
        num_val = request.form.get("num_val")
        price = request.form.get("price")
        accessibility = request.form.get("accessibility")
        duration = request.form.get("duration")
        slider_mode = request.form.get("slider_mode")

    # arrays of options for sliders--index corresponds to chosen option
    num_val_options = ["1", "2", "3", "4", "5", "6", "8"]
    accessibility_options = ["few to no challenges", "minor challenges", "some challenges"]
    duration_options = ["minutes", "hours"]

    return render_template("activities.html", username=session['username'], data=data, num_val=num_val, price=price, accessibility=accessibility, duration=duration, slider_mode=slider_mode)

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
