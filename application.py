import os

from flask import Flask, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from forms import LoginForm, RegisterForm

app = Flask(__name__)

# Change in production
app.secret_key = 'secret'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route("/register")
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)
