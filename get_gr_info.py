from application import db
from get_gr_author_info import run


def start():
    a_q = db.execute(
        'SELECT * '
        'FROM public.author '
        'WHERE id BETWEEN 501 AND 1935'
    ).fetchall()

    for a in a_q:
        gr_info = run(a.name)

        db.execute(
            'INSERT INTO public.author_gr_map (author_id, author_id_gr, author_ph_gr)'
            'VALUES (:author_id, :author_id_gr, :author_ph_gr)',
            {"author_id": a.id,
             "author_id_gr": gr_info[0],
             "author_ph_gr": gr_info[1]}
        )
        db.commit()
        print(f'Inserted: id: {a.id}, gr_id: {gr_info[0]} src: {gr_info[1]}')


if __name__ == '__main__':
    start()
