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
import html

OPENTDB_COOLDOWN = 5.1
trivia_opentdb_call = 0.0

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
    global trivia_opentdb_call
    now = time.monotonic()
    wait = OPENTDB_COOLDOWN - (now - trivia_opentdb_call)
    if wait > 0:
        time.sleep(wait)
    trivia_opentdb_call = time.monotonic()
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
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "GET":
        return render_template(
            "trivia.html",
            username=username,
            stage="choose",
            points=data.get_score(username)
        )

    action = request.form.get("action", "")
    chosen = request.form.get("difficulty") or request.form.get("current_difficulty") or "easy"
    if chosen not in ["easy", "medium", "hard"]:
        chosen = "easy"

    message = ""

    if action == "answer":
        user_answer = request.form.get("answer", "")
        correct = session.get("trivia_correct")
        difficulty = session.get("trivia_difficulty", chosen)

        if correct is not None and user_answer == correct:
            pts_map = {"easy": 10, "medium": 20, "hard": 30}
            pts = pts_map.get(difficulty, 10)
            data.add_to_score(username, pts)
            message = f"Correct! +{pts} points."
        else:
            message = f"Incorrect. Correct answer: {html.unescape(correct) if correct else ''}"

    trivia_data = get_trivia_question(chosen)
    if trivia_data == url_err:
        return render_template("keyerror.html", API="opentdb", err=trivia_data)

    q = trivia_data["results"][0]

    question = html.unescape(q["question"])
    category = html.unescape(q["category"])
    difficulty = html.unescape(q["difficulty"])
    correct_answer = html.unescape(q["correct_answer"])

    answers = [html.unescape(a) for a in q["incorrect_answers"]]
    answers.append(correct_answer)
    random.shuffle(answers)

    session["trivia_correct"] = correct_answer
    session["trivia_difficulty"] = chosen

    return render_template(
        "trivia.html",
        username=username,
        stage="question",
        chosen_difficulty=chosen,
        points=data.get_score(username),
        message=message,
        q={
            "question": question,
            "category": category,
            "difficulty": difficulty
        },
        answers=answers
    )

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
