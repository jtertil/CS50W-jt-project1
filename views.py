import requests

from flask import request, render_template, redirect, url_for, session,\
    flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import abort

from application import app, db, is_isbn_code, login_only, gr_api_key
from forms import LoginForm, RegisterForm, SearchForm, ReviewForm


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
            session['user_id'] = u.id
            flash(f"logged as {session['user']}", 'debug')
            return redirect(url_for('search'))

    else:
        return render_template('login.html', form=form)


@app.route('/logout')
@login_only
def logout():
    session['user'] = None
    flash(f"logged as {session['user']}", 'debug')
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
@login_only
def search():
    form = SearchForm()
    print('user' in session)
    if request.method == 'POST' and form.validate_on_submit():
        user_provides_isbn = is_isbn_code(form.search.data)

        if user_provides_isbn:
            return redirect(url_for('book', book_isbn=user_provides_isbn))

        else:
            s_q_authors = db.execute(
                'SELECT * FROM public.author '
                'WHERE LOWER(name) LIKE LOWER(:search_like) ',
                {'search_like': '%'+form.search.data+'%'}
            ).fetchall()

            s_q_books = db.execute(
                'SELECT public.book.*, '
                'array_agg(public.author.name) '
                'FROM public.book '
                'JOIN public.book_author '
                'ON public.book.id = public.book_author.book_id '
                'JOIN public.author '
                'ON public.book_author.author_id = public.author.id '
                'WHERE isbn LIKE :search_like '
                'OR to_tsvector(title) @@ to_tsquery(:search) '
                'GROUP BY public.book.id',
                {'search': form.search.data,
                 'search_like': '%'+form.search.data+'%'}
            ).fetchall()

            results = (s_q_books, s_q_authors)
            return render_template('search.html', form=form, results=results)

    if not form.validate_on_submit():
        flash(f"validation error: {form.errors}", 'debug')

    return render_template('search.html', form=form)


@app.route('/book/<string:book_isbn>', methods=['GET', 'POST'])
@login_only
def book(book_isbn):
    form = ReviewForm()

    try:
        book_json = requests.get(
            f'http://localhost:5000/api/{book_isbn}').json()
    # TODO exception to broad
    except:
        abort(404)

    try:
        gr_api_json = requests.get(
            "https://www.goodreads.com/book/review_counts.json",
            params={"key": gr_api_key, "isbns": book_isbn}).json()
    # TODO exception to broad
    except:
        gr_api_json = None

    book_id = db.execute(
        'SELECT id FROM public.book '
        'WHERE isbn = :isbn',
        {'isbn': book_json['isbn']}
    ).fetchone()

    r_q = db.execute(
        'SELECT public.user_book.*, '
        'public.user.name '
        'FROM public.user_book '
        'JOIN public.user '
        'ON public.user.id = public.user_book.user_id '
        'WHERE book_id = :book_id '
        'ORDER BY (id) DESC ',
        {"book_id": book_id[0]}
    ).fetchall()

    # TODO avoid resending api requests in case of page reload
    if request.method == 'POST' and form.validate_on_submit():
        db.execute(
            'INSERT INTO public.user_book (user_id, book_id, score, review) '
            'VALUES (:user_id, :book_id, :score, :review) '
            'ON CONFLICT (user_id, book_id) '
            'DO UPDATE SET score = :score, review = :review',
            {"user_id": session['user_id'],
             "book_id": book_id[0],
             "score": form.rating.data,
             "review": form.review.data
             })
        db.commit()
        return redirect(url_for('book', book_isbn=book_isbn))

    reviews = []
    already_review = False
    for r in r_q:
        if r[5] == session['user']:
            already_review = True
            form.review.default = r[4]
            form.rating.default = int(r[3])
            form.process()
        reviews.append({'user': r[5], 'rating': r[3], 'review': r[4]})

    return render_template(
        'book.html',
        form=form,
        book_json=book_json,
        gr_api_json=gr_api_json,
        reviews=reviews,
        already_review=already_review
    )
