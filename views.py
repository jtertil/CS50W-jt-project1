from flask import request, render_template, redirect, url_for, session,\
    flash
from werkzeug.security import generate_password_hash, check_password_hash

from application import app, db, is_isbn_code, login_only
from forms import LoginForm, RegisterForm, SearchForm


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
            s_q = db.execute(
                'SELECT * FROM public.book '
                'WHERE isbn = :isbn',
                {"isbn": user_provides_isbn}
            ).fetchone()
            # TODO redirect directly to book page
            return str(s_q)
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
