import unittest
from application import app, is_isbn_code, login_only
from flask import session


class TestViews(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_index_get_response(self):
        r = self.app.get('/')
        self.assertEqual(200, r.status_code)

    def test_index_post_response(self):
        r = self.app.post('/')
        self.assertEqual(405, r.status_code)

    def test_login_get_response(self):
        r = self.app.get('/login')
        self.assertEqual(200, r.status_code)

    def test_login_post_response(self):
        r = self.app.post('/login')
        self.assertEqual(200, r.status_code)

    def test_register_get_response(self):
        r = self.app.get('/register')
        self.assertEqual(200, r.status_code)

    def test_register_post_response(self):
        r = self.app.post('/register')
        self.assertEqual(200, r.status_code)

    def test_logout_get_response(self):
        r = self.app.get('/logout')
        self.assertEqual(302, r.status_code)

    def test_logout_post_response(self):
        r = self.app.post('/logout')
        self.assertEqual(405, r.status_code)

    def test_search_get_response(self):
        r = self.app.get('/search')
        self.assertEqual(302, r.status_code)

    def test_search_post_response(self):
        r = self.app.post('/search')
        self.assertEqual(302, r.status_code)

    def test_book_get_response_empty(self):
        r = self.app.get('/book')
        self.assertEqual(404, r.status_code)

    def test_book_get_response(self):
        r = self.app.get('/book/0380795272')
        self.assertEqual(302, r.status_code)

    def test_book_post_response(self):
        r = self.app.post('/book/0380795272')
        self.assertEqual(302, r.status_code)

    def test_author_get_response_empty(self):
        r = self.app.get('/author')
        self.assertEqual(404, r.status_code)

    def test_author_get_response(self):
        r = self.app.get('/author/1')
        self.assertEqual(302, r.status_code)

    def test_author_post_response(self):
        r = self.app.post('/author/0380795272')
        self.assertEqual(405, r.status_code)


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_empty_not_isbn(self):
        check = is_isbn_code('')
        self.assertEqual(False, check)

    def test_author_not_isbn(self):
        check = is_isbn_code('Raymond E. Feist')
        self.assertEqual(False, check)

    def test_title_not_isbn(self):
        check = is_isbn_code('Krondor: The Betrayal')
        self.assertEqual(False, check)

    def test_isbn10_is_isbn(self):
        check = is_isbn_code('0380795272')
        self.assertEqual('0380795272', check)

    def test_isbn13_is_isbn(self):
        check = is_isbn_code('9780380795277')
        self.assertEqual('0380795272', check)

    def test_isbn_cleanup(self):
        check = is_isbn_code('#0-380-79527-2/')
        self.assertEqual('0380795272', check)


class TestFuncDeco(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        with app.test_request_context():
            session['user'] = None

    def test_func_wo_dec_returns_1(self):

        def func():
            return 1

        check = func()
        self.assertEqual(1, check)

    def test_func_w_dec_returns_302(self):
        with app.test_request_context():

            @login_only
            def func():
                return 1

            check = func()
        self.assertEqual(302, check.status_code)

    def test_func_w_dec_returns_1_when_session(self):
        with app.test_request_context():
            session['user'] = 'test'

            @login_only
            def func():
                return 1

            check = func()
        self.assertEqual(1, check)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_api_404_response(self):
        r = self.app.get('/api/wrongisbn')
        self.assertEqual(404, r.status_code)

    def test_api_get_response(self):
        r = self.app.get('/api/0380795272')
        self.assertEqual(200, r.status_code)

    def test_api_return_json(self):
        r = self.app.get('/api/0380795272')
        self.assertEqual(True, r.is_json)

    def test_api_json_keys(self):
        r = self.app.get('/api/0380795272')
        expected_json_keys = [
            'author', 'average_score', 'isbn', 'review_count', 'title', 'year']
        actual_json_keys = r.get_json().keys()
        # symmetric difference should be an empty list (no difference)
        diff = set(expected_json_keys) ^ set(actual_json_keys)
        self.assertEqual(set(), diff)

    def test_api_post_response(self):
        r = self.app.post('/api/0380795272')
        self.assertEqual(405, r.status_code)


if __name__ == '__main__':
    unittest.main()
