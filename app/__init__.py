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
import json
import sqlite3
import data

data.create_user_data()
DB_FILE="data.db"

app = Flask(__name__)
app.secret_key = "secret"

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
        #if not username or not password:
        #    return render_template('login.html', error="No username or password inputted")

        #search user table for password from a certain username
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        account = c.execute("SELECT password FROM userdata WHERE username = ?", (username,)).fetchone()
        db.close()

        #if there is no account then reload page
        #if account is None:
        #    return render_template("login.html", error="Username or password is incorrect")

        # check if password is correct, if not then reload page
        #if account[0] != password:
        #    return render_template("login.html", error="Username or password is incorrect")

        # if password is correct redirect home
        session["username"] = username
        return redirect(url_for("home"))

    return render_template('login.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('home.html', username=session['username'])


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # reload page if no username or password was entered
        #if not username or not password:
        #    return render_template("register.html", error="No username or password inputted")

        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        # check if username already exists and reload page if it does
        #exists = c.execute("SELECT 1 FROM userdata WHERE name = ?", (username,)).fetchone()
        #if exists:
        #    db.close()
        #    return render_template("register.html", error="Username already exists")

        c.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        db.close()

        session['username'] = username
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('username', None) # remove username from session
    return redirect(url_for('login'))

def get_trivia_question():

    url = f"https://opentdb.com/api.php?amount=1" # Endpoint URL

    response = urllib.request.urlopen(url) # This sends the HTTP GET request to Nasa API and urlopen returns a response obj.
    data = json.loads(response.read().decode()) # This decodes the response, which is in bytes, into string and then loads the json string into a python dictionary: data.
    
    print(data)
    return data   # Returning the python dictionary for route.

@app.route("/trivia")
def main():
    trivia_data = get_trivia_question()
    print(data)
    return render_template("trivia.html", trivia=trivia_data)  

if __name__=='__main__':
    app.debug = True
    app.run()
