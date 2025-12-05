from flask import Flask 
from flask import render_template 
from flask import request, redirect, url_for  
from flask import session
import sqlite3

DB_FILE="discobandit.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
db.row_factory = sqlite3.Row
c = db.cursor()

c.execute("create table if not exists entries(user_id integer, title text, post text, timestamp date, last_edit date, id integer primary key);")
c.execute("create table if not exists account(username text, email text, password text, first_name text, last_name text, id integer primary key);")
db.commit()

app = Flask(__name__)  # create Flask object


if __name__ == "__main__":  # false if this file imported as module
    app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run()
