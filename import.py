import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():

    def make_authors_list(string):
        """
        split to list to prevent records with multiple authors,
        call on each clean_whitespaces,
        and returns a list
        """
        return [clean_whitespaces(a) for a in string.split(', ')]

    def clean_whitespaces(string):
        """removes multiple spaces and return string"""
        return " ".join(string.split())

    def build_list_of_books(file):
        """
        convert csv input file,
        run helpers functions
        and return a list
        [[b1_isbn, b1_title, [b1_author1, b1_author2], b1_year], [...], ]
        """
        reader = csv.reader(file)
        books = []

        for row in reader:
            try:
                books.append([
                    row[0],
                    clean_whitespaces(row[1]),
                    make_authors_list(row[2]),
                    int(row[3])
                ])
            except ValueError:
                print(f"Err, skipping: {row[0]} {row[1]} {row[2]} {row[3]}")

        return books

    def update_authors(list_of_books):
        """
        create a list of authors from a list of books,
        insert authors into db, skipping existing ones
        """
        import_authors = []
        for book in list_of_books:
            for a in book[2]:
                import_authors.append(a)
        inserted = 0
        skipped = 0
        for a in import_authors:
            already_exist = db.execute(
                'SELECT * FROM author '
                'WHERE name = :name',
                {"name": a}
            ).fetchone()
            if already_exist:
                skipped += 1
            else:
                db.execute(
                    'INSERT INTO author (name) '
                    'VALUES (:name)',
                    {"name": a})
                inserted += 1
        db.commit()
        print(
            f'Authors update done (inserted:{inserted}, skipped: {skipped}).'
        )

    def update_books(list_of_books):
        """
        insert books into db, skipping existing ones,
        insert book-author relation into db
        """
        inserted = 0
        skipped = 0

        for book in list_of_books:
            already_exist = db.execute(
                'SELECT * FROM book '
                'WHERE isbn = :isbn',
                {"isbn": book[0]}
            ).fetchone()
            if already_exist:
                skipped += 1
            else:
                db.execute(
                    'INSERT INTO book (isbn, title, year)'
                    'VALUES (:isbn, :title, :year)',
                    {"isbn": book[0], "title": book[1], "year": book[3]}
                )
                db.commit()

                book_id = db.execute(
                    'SELECT id FROM book '
                    'WHERE isbn = :isbn',
                    {"isbn": book[0]}
                ).fetchone()[0]

                for author in book[2]:
                    author_id = db.execute(
                        'SELECT id FROM author '
                        'WHERE name = :name',
                        {"name": author}
                    ).fetchone()[0]

                    db.execute(
                        'INSERT into book_author (book_id, author_id)'
                        'VALUES (:book_id, :author_id)',
                        {"book_id": book_id, "author_id": author_id}
                    )
                    db.commit()
                    inserted += 1
        print(f'Books update done (inserted:{inserted}, skipped: {skipped}).')

    file = open("books.csv")
    list_of_books = build_list_of_books(file)

    update_authors(list_of_books)
    update_books(list_of_books)


if __name__ == "__main__":
    main()
