from flask import request, render_template, redirect, url_for, session,\
    flash
from werkzeug.security import generate_password_hash, check_password_hash

from application import app, db
from forms import LoginForm, RegisterForm, SearchForm

from isbnlib import is_isbn10, is_isbn13, to_isbn10


def is_isbn_code(search):
    """checks if the received string is valid isbn number"""
    check = ''.join(ch for ch in search if ch.isalnum())

    if is_isbn13(check):
        return to_isbn10(check)

    if is_isbn10(check):
        return check

    else:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        u = db.execute(
            'SELECT * FROM public.user '
            'WHERE name = :name',
            {"name": form.login.data}
        ).fetchone()

        if u:
            flash('user already exist', 'debug')
            return render_template('register.html', form=form)

        db.execute(
            'INSERT INTO public.user (name, hash)'
            'VALUES (:name, :hash)',
            {"name": form.login.data,
             "hash": generate_password_hash(form.passw.data)}
        )
        db.commit()
        flash('registration ok', 'debug')
        return redirect(url_for('index'))

    else:
        flash(form.errors, 'debug')
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        u = db.execute(
            'SELECT * FROM public.user '
            'WHERE name = :name',
            {"name": form.login.data}
        ).fetchone()

        if not u:
            flash('no user', 'debug')
            return render_template('login.html', form=form)

        if not check_password_hash(u[2], request.form['passw']):
            flash('no password match', 'debug')
            return render_template('login.html', form=form)

        elif check_password_hash(u[2], request.form['passw']):
            session['user'] = request.form['login']
            flash(f"logged as {session['user']}", 'debug')
            return redirect(url_for('index'))

    else:
        return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session['user'] = None
    flash(f"logged as {session['user']}", 'debug')
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        if is_isbn_code(form.search.data):
            return 'isbn'
        else:
            return 'not isbn'

    return render_template('search.html', form=form)
