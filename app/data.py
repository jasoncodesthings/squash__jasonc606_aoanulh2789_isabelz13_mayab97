# Squash (Jason Chan, Aoanul Hoque, Isabel Zheng, Maya Berchin)
# p01
# SoftDev
# 11/25/25--2025-12-22
# Time spent: not that much on this file tbh, mostly recycling. ~40 mins?

import sqlite3                      # enable control of an sqlite database
import hashlib                      #for consistent hashes


#=============================MAKE=TABLES=============================#


# make the database table we need if it doesn't already exist

# userdata
def create_user_data():

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS userdata (
            username TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL,
            trivia_score INT
        )"""
    )

    db.commit()
    db.close()




#=============================USERDATA=============================#


#----------USERDATA-ACCESSORS----------#


# returns a list of usernames
def get_all_users():
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    data = c.execute('SELECT username FROM userdata').fetchall()

    db.commit()
    db.close()

    return clean_list(data)


def get_score(username):
    return get_field('userdata', 'username', username, 'trivia_score')


#----------USERDATA-MUTATORS----------#


def add_to_score(username, points):
    score = get_score(username)
    score += points
    if score >= 0:
        modify_field("userdata", "username", username, "trivia_score", score)
        return "success"
    return "failure"


#----------LOGIN-REGISTER-AUTH----------#


# returns whether or not a user exists
def user_exists(username):
    all_users = get_all_users()
    for user in all_users:
        if (user == username):
            return True
    return False


# checks if provided password in login attempt matches user password
def auth(username, password):
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    if not user_exists(username):
        db.commit()
        db.close()

        #raise ValueError("Username does not exist")
        return False

    # use ? for unsafe/user provided variables
    passpointer = c.execute('SELECT password FROM userdata WHERE username = ?', (username,))
    real_pass = passpointer.fetchone()[0]

    db.commit()
    db.close()

    password = password.encode('utf-8')

    # hash password here
    if real_pass != str(hashlib.sha256(password).hexdigest()):
        #raise ValueError("Incorrect password")
        return False

    return True


# adds a new user's data to user table
def register_user(username, password):

    if user_exists(username):
        #raise ValueError("Username already exists")
        return "Username already exists"

    #if password == "":
        #raise ValueError("You must enter a non-empty password")
        #return "You must enter a non-empty password"

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # hash password here
    password = password.encode('utf-8')
    password = str(hashlib.sha256(password).hexdigest())

    # use ? for unsafe/user provided variables
    c.execute('INSERT INTO userdata VALUES (?, ?, 0)', (username, password,))

    db.commit()
    db.close()

    return "success"


#=============================GENERAL=HELPERS=============================#


# wrapper method
# used for a bunch of accessor methods; used when only 1 item should be returned
def get_field(table, ID_fieldname, ID, field):
    lst = get_field_list(table, ID_fieldname, ID, field)
    if (len(lst) == 0):
        return 'None'
    return lst[0]


# used for a bunch of accessor methods; used when a list of items in a certain field should be returned
def get_field_list(table, ID_fieldname, ID, field):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    data = c.execute(f'SELECT {field} FROM {table} WHERE {ID_fieldname} = ?', (ID,)).fetchall()

    db.commit()
    db.close()

    return clean_list(data)


# turn a list of tuples (returned by .fetchall()) into a 1d list
def clean_list(raw_output):

    clean_output = []

    for lst in raw_output:
        for item in lst:
            if str(item) != 'None':
                clean_output += [item]

    return clean_output


def modify_field(table, ID_fieldname, ID, field, new_val):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # use ? for unsafe/user provided variables
    c.execute(f'UPDATE {table} SET {field} = ? WHERE {ID_fieldname} = ?', (new_val, ID,))

    db.commit()
    db.close()


#=============================MAIN=SCRIPT=============================#

# make table
create_user_data()
