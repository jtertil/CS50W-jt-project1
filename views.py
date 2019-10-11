from json import JSONDecodeError
import requests
from xml.etree.ElementTree import fromstring, ElementTree

from flask import request, render_template, redirect, url_for, session,\
    flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import abort, HTTPException

from application import app, db, is_isbn_code, login_only, gr_api_key
from forms import LoginForm, RegisterForm, SearchForm, ReviewForm


@app.route('/')
def index():

    q = db.execute(
        'SELECT title '
        'FROM public.book '
        'ORDER BY random() '
        'LIMIT 15;').fetchall()

    rnd_titles = [t[0] + '?' for t in q]
    return render_template('index.html', rnd_titles=rnd_titles)


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
            flash(f'username {form.login.data} not available', 'alert')
            return render_template('register.html', form=form)

        db.execute(
            'INSERT INTO public.user (name, hash)'
            'VALUES (:name, :hash)',
            {"name": form.login.data,
             "hash": generate_password_hash(form.passw.data)}
        )
        db.commit()
        flash(
            'Registration completed successfully. '
            'Now you can <a href="./login" class="alert-link">login</a>.',
            'success')
        return redirect(url_for('index'))

    else:
        for field in form.errors:
            for err in form.errors[field]:
                flash(f'{field}: {err}', 'alert')

        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    session['user'] = None
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
            flash(f'login and password no match', 'alert')
            return render_template('login.html', form=form)

        elif check_password_hash(u[2], request.form['passw']):
            session['user'] = request.form['login']
            session['user_id'] = u.id
            return redirect(url_for('search'))

    else:
        for field in form.errors:
            for err in form.errors[field]:
                flash(f'{field}: {err}', 'alert')
        return render_template('login.html', form=form)


@app.route('/logout')
@login_only
def logout():
    session['user'] = None
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
@login_only
def search():
    form = SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_provides_isbn = is_isbn_code(form.search.data)

        if user_provides_isbn:
            return redirect(url_for('book', book_isbn=user_provides_isbn))

        else:
            s_q_authors = db.execute(
                'SELECT *, '
                'public.author_gr_map.author_id_gr, '
                'public.author_gr_map.author_ph_gr '
                'FROM public.author '
                'LEFT JOIN public.author_gr_map '
                'ON public.author.id = public.author_gr_map.author_id '
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
                {'search': form.search.data.strip().replace(' ', ' & '),
                 'search_like': '%'+form.search.data+'%'}
            ).fetchall()

            results = (s_q_books, s_q_authors)
            return render_template('search.html', form=form, results=results)

    if not form.validate_on_submit():
        flash(f"validation error: {form.errors}", 'debug')
        for field in form.errors:
            for err in form.errors[field]:
                flash(f'{field}: {err}', 'alert')

    return render_template('search.html', form=form, results=None)


@app.route('/book/<string:book_isbn>', methods=['GET', 'POST'])
@login_only
def book(book_isbn):
    form = ReviewForm()

    r_api = requests.get(f'http://localhost:5000/api/{book_isbn}')
    if r_api.status_code != 200:
        return abort(404)

    try:
        book_json = r_api.json()
    except JSONDecodeError:
        return abort(500)

    r_gr_api = requests.get(
            "https://www.goodreads.com/book/review_counts.json",
            params={"key": gr_api_key, "isbns": book_isbn})

    try:
        gr_api_json = r_gr_api.json()
    except JSONDecodeError:
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
    for r_api in r_q:
        if r_api[5] == session['user']:
            already_review = True
            form.review.default = r_api[4]
            form.rating.default = int(r_api[3])
            form.process()
        reviews.append(
            {'user': r_api[5], 'rating': r_api[3], 'review': r_api[4]})

    flash(f"validation error: {form.errors}", 'debug')
    return render_template(
        'book.html',
        form=form,
        book_json=book_json,
        gr_api_json=gr_api_json,
        reviews=reviews,
        already_review=already_review
    )


@app.route('/author/<string:author_id>', methods=['GET'])
@login_only
def author(author_id):

    a_q = db.execute(
        'SELECT public.author.id, '
        'public.author.name, '
        'public.author_gr_map.author_id_gr, '
        'public.author_gr_map.author_ph_gr '
        'FROM public.author '
        'LEFT JOIN public.author_gr_map '
        'ON public.author.id = public.author_gr_map.author_id '
        'WHERE public.author.id = :author_id ',
        {'author_id': int(author_id)}
    ).fetchone()

    try:
        r = requests.get(
            f'https://www.goodreads.com/author/show/'
            f'{a_q.author_id_gr}?format=xml&key={gr_api_key}')
        tree = ElementTree(fromstring(r.text))
        root = tree.getroot()
        dsc = root[1][8].text

    # # TODO bare except
    except:
        dsc = None

    a_books = db.execute(
       'SELECT public.book.* '
       'FROM public.book_author '
       'JOIN public.book '
       'ON public.book.id = public.book_author.book_id '
       'WHERE author_id = :author_id '
       'ORDER BY (year) DESC ',
       {'author_id': int(author_id)}
    ).fetchall()

    return render_template(
        'author.html',
        a_q=a_q,
        dsc=dsc,
        a_books=a_books)


@app.errorhandler(Exception)
def error(err):
    if isinstance(err, HTTPException):
        return render_template('error.html', http_err=err), err.code

    # non-HTTP exceptions
    print(err)
    return render_template('error.html')
