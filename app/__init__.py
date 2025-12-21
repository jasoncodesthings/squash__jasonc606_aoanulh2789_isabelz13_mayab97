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
import random

OPENTDB_COOLDOWN = 5.1 # Cooldown to avoid hitting rate limits
trivia_opentdb_call = 0.0 # stores the last OpenTDB call

TRIVIA_POOL = {"easy": [], "medium": [], "hard": []} # question bank that stores the batch of questions (10 in our case). This makes it easier to fetch questions.

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
    global trivia_opentdb_call  # Global so it can update trivia_opentdb_call
    now = time.monotonic() # time_opentdb_call uses time.monotonic(). It's ideal to use this since we only need to track elapsed time
    wait = OPENTDB_COOLDOWN - (now - trivia_opentdb_call)
    if wait > 0:
        time.sleep(wait)
    trivia_opentdb_call = time.monotonic()
    return get_data(url) # fetches json if cooldown expires

def refill_pool(difficulty, amount=10):
    url = f"https://opentdb.com/api.php?amount={amount}&difficulty={difficulty}" # api endpoint
    for _ in range(3): # a for loop to error handle, we send OpenTDB a request up to 3  times if  an error is hit, if not we continue and refill the pool
        data = opentdb_get(url)
        if data == url_err: #if there's any error fetching the json we continue
            continue
        if data.get("response_code") == 5:
            time.sleep(OPENTDB_COOLDOWN) #  If this is hit it means a ratelimit occured
            continue
        if data.get("response_code") == 0 and data.get("results"):
            TRIVIA_POOL[difficulty].extend(data["results"]) # Response code 0 indicates success
            return True
    return False # If true isn't returned that means OpenTDB did not refill the pool of questions, we need to try again.


def get_trivia_question(difficulty=None):
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "easy" #if no difficulty is selected (error handle) it'll  be easy automatically

    if not TRIVIA_POOL[difficulty]: #if the trivia pool is empty we attempt to refill the pool
        ok = refill_pool(difficulty, amount=10)
        if not ok:
            return url_err #returns url_err if the refill fails

    q = TRIVIA_POOL[difficulty].pop(0) #If we have a pool we pop (get rid of the first index) to the next question
    return {"response_code": 0, "results": [q]} #Wrapping  the question that matches the OpenTDB json

@app.route("/trivia", methods=["GET", "POST"])
def trivia():
    if "username" not in session:  # login handling
        return redirect(url_for("login"))

    user = session["username"]

    if request.method == "GET":  # Get request telling us what to display  "choose" which is the difficulty section and points
        return render_template(
            "trivia.html",
            username=user,
            stage="choose",
            points=data.get_score(user)
        )

    chosen = request.form.get("difficulty") or request.form.get("current_difficulty")
    if chosen not in ["easy", "medium", "hard"]:
        chosen = "easy"  # Determining difficulty

    picked = request.form.get("answer")  # Get the selected answer from the form
    if picked:  # Score the submitted answer, picked = the answer  submitted
        correct = session.get("trivia_correct")  # trivia_correct grabs the actual answer
        last_diff = session.get("trivia_difficulty", chosen)

        if correct and picked == correct:  # If the answer is correct, then award points
            pts = {"easy": 10, "medium": 20, "hard": 30}[last_diff]
            data.add_to_score(user, pts)

    trivia_data = get_trivia_question(chosen)  # Gets the next question via pop or refills
    if trivia_data == url_err:
        return render_template("keyerror.html", API="opentdb", err=trivia_data)  # if url_err is returned we contact trivia.html basically to display error

    q = trivia_data["results"][0]  # Question and  answer choices
    session["trivia_correct"] = q["correct_answer"]  # Right  answer
    session["trivia_difficulty"] = chosen  # Difficulty

    return render_template(
        "trivia.html",
        username=user,
        trivia=trivia_data,
        stage="question",
        chosen_difficulty=chosen,
        points=data.get_score(user)
    )

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    if "username" not in session:  # login handling
        return redirect(url_for("login"))

    # Get the top 10 players from the database
    top_players = data.get_top_players()

    return render_template(
        "leaderboard.html",
        username=session["username"],  # Pass current username to leaderboard.html
        top_players=top_players  # Pass the top 10 players to leaderboard.html
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

    if "username" not in session:  # login handling
        return redirect(url_for("login"))

    # get values for sliders. set to default
    category = "any"
    num_val = 1
    price = 10
    accessibility = 1
    duration = 0
    child_friendly = 0
    if "category" in request.form:
        category = request.form.get("category")
    if "num_val" in request.form:
        # all values in here/not the first time loading this page
        num_val = int(request.form.get("num_val"))
        price = int(request.form.get("price"))
        accessibility = int(request.form.get("accessibility"))
    if "duration" in request.form:
        duration = 1
    if "child_friendly" in request.form:
        child_friendly = 1

    # arrays of options for sliders--index corresponds to chosen option
    category_options = ["any", "education", "recreational", "social", "charity", "cooking", "relaxation", "busywork"]
    num_val_options = [1, 2, 3, 4, 5, 6, 8]
    price_options = [i for i in range(40)]
    for i in range(len(price_options)):
        price_options[i] *= 0.01
        price_options[i] = float("{:.2f}".format(price_options[i]))
    price_options += [1.0]
    accessibility_options = ["Few to no challenges", "Minor challenges", "Some challenges", "Major challenges"]
    duration_options = ["minutes", "hours"]

    url = f"https://bored-api.appbrewery.com/filter?participants={num_val_options[num_val]}"
    if category != "any":
        url += f"&type={category}"

    data_lst = get_data(url)
    
    # select a random item from data_lst
    data = ""
    if data_lst != url_err:
        
        while len(data) == 0 and len(data_lst) > 0:
            item = random.choice(data_lst)
            # check if this item fulfills the conditions
            try:
                if not (float(item["price"]) > price_options[price] or accessibility_options.index(item["accessibility"]) > accessibility or item["duration"] != duration_options[duration]):
                    data = item
            except ValueError:
                pass
            data_lst.remove(item)
        
        price_options[len(price_options)-1] = "0.4+"
        return render_template("activities.html", username=session['username'], data=data, category=category, category_options=category_options, num_val=num_val, num_val_options=json.dumps(num_val_options), price=price, price_options=json.dumps(price_options), accessibility=accessibility, accessibility_options=json.dumps(accessibility_options), duration=duration, child_friendly=child_friendly)
    
    else: # url_err
        return render_template("keyerror.html", API="Bored API", err=data_lst)

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
