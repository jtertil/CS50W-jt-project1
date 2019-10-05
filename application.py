import os

from flask import Flask, session, redirect, url_for, flash
from logging import FileHandler, WARNING
from functools import wraps

from isbnlib import is_isbn13, to_isbn10, is_isbn10
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True

# Error Log:
if not app.debug:
    f_handler = FileHandler('error_log.txt')
    f_handler.setLevel(WARNING)
    app.logger.addHandler(f_handler)

# Change in production
app.secret_key = 'secret'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set up Goodreads API
gr_api_key = os.getenv("GR_API_KEY")


def is_isbn_code(search):
    """checks if the received string is valid isbn number"""
    check = ''.join(ch for ch in search if ch.isalnum())

    if is_isbn13(check):
        return to_isbn10(check)

    if is_isbn10(check):
        return check

    else:
        return False


def login_only(view):
    @wraps(view)
    def wrap(*args, **kwargs):
        try:
            if session['user']:
                return view(*args, **kwargs)
            else:
                flash('login first', 'debug')
                return redirect(url_for('login'))
        except KeyError:
            return redirect(url_for('login'))

    return wrap


import views  # noqa: F401
import api  # noqa: F401
