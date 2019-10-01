import os

from flask import Flask, request, render_template, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

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

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        u = db.execute(
                'SELECT * FROM public.user '
                'WHERE name = :name',
                {"name": form.login.data}
            ).fetchone()

        if not u:
            print('no user')
            return render_template('login.html', form=form)

        if not check_password_hash(u[2], request.form['passw']):
            print('no password match')
            return render_template('login.html', form=form)

        elif check_password_hash(u[2], request.form['passw']):
            session['user'] = request.form['login']
            print(session['user'])
            return redirect(url_for('index'))

    else:
        return render_template('login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        u = db.execute(
                'SELECT * FROM public.user '
                'WHERE name = :name',
                {"name": form.login.data}
            ).fetchone()

        if u:
            print('user already exist')
            return render_template('register.html', form=form)

        db.execute(
            'INSERT INTO public.user (name, hash)'
            'VALUES (:name, :hash)',
            {"name": form.login.data,
             "hash": generate_password_hash(form.passw.data)}
        )
        db.commit()
        print('registration ok')
        return redirect(url_for('index'))

    else:
        print(form.errors)
        return render_template('register.html', form=form)
