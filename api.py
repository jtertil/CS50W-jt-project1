from werkzeug.exceptions import abort
from application import app, db


@app.route('/api/<string:book_isbn>', methods=['GET'])
def api(book_isbn):
    # query db to check is book with provided isb exist in db
    book = db.execute(
        'SELECT * FROM public.book '
        'WHERE isbn = :isbn',
        {'isbn': book_isbn}
    ).fetchone()

    if not book:
        abort(404)

    # query db to get authors id's for current book
    query_author_ids = db.execute(
        'SELECT author_id FROM public.book_author '
        'WHERE book_id = :book_id',
        {'book_id': book.id}
    ).fetchall()
    author_ids = [a[0] for a in query_author_ids]

    # query db to get authors
    authors = []
    for author_id in author_ids:
        q_a = db.execute(
            'SELECT name FROM public.author '
            'WHERE id = :author_id',
            {'author_id': author_id}
        ).first()
        authors.append({'id': author_id, 'name': q_a[0]})

    # query db to get review count
    r_c = db.execute(
        'SELECT COUNT (id) FROM public.user_book WHERE book_id = :book_id',
        {'book_id': book.id}
    ).fetchone()

    # query db to get average score
    r_s = db.execute(
        'SELECT AVG (score) FROM public.user_book WHERE book_id = :book_id',
        {'book_id': book.id}
    ).fetchone()

    book_json = {'title': book.title,
                 'author': authors,
                 'isbn': book.isbn,
                 'year': book.year,
                 "review_count": r_c[0],
                 "average_score": round(r_s[0], 1) if r_s[0] else None
                 }

    return book_json
