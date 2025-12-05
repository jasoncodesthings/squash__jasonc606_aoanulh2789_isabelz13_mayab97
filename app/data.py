# Squash (Jason Chan, Aoanul Hoque, Isabel Zheng, Maya Berchin)
# p01
# SoftDev

import sqlite3   #enable control of an sqlite database
import secrets  # used to generate ids
from datetime import datetime # for user signup date
import hashlib   #for consistent hashes


#=============================MAKE=TABLES=============================#

# make the database tables we need if they don't already exist

# userdata
def create_user_data():

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS userdata (
            username TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL,
            sign_up_date DATE NOT NULL,
            bio TEXT,
            trivia_score INT
        )"""
    )

    db.commit()
    db.close()
