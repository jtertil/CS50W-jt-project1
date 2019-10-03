from flask import request, render_template, redirect, url_for, session,\
    flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

from application import app, db
from forms import LoginForm, RegisterForm


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


@app.route('/book/<string:book_isbn>')
def book(book_isbn):
    book = db.execute(
        'SELECT * FROM public.book '
        'WHERE isbn = :isbn',
        {'isbn': book_isbn}
    ).fetchone()

    if not book:
        abort(404)

    query_author_ids = db.execute(
        'SELECT author_id FROM public.book_author '
        'WHERE book_id = :book_id',
        {'book_id': book.id}
    ).fetchall()

    author_ids = [a[0] for a in query_author_ids]

    authors = []
    for author_id in author_ids:
        q_a = db.execute(
            'SELECT name FROM public.author '
            'WHERE id = :author_id',
            {'author_id': author_id}
        ).first()
        authors.append(q_a[0])

    return "BookID: {}, ISBN: {}, Title: {}, Author(s): {}, Year: {}".format(
        book.id, book.isbn, book.title, ", ".join(authors), book.year)