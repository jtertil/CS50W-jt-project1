import unittest
from application import app


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

    def test_book_404_response(self):
        r = self.app.get('/book/fakeisbn')
        self.assertEqual(404, r.status_code)

    def test_book_get_response(self):
        r = self.app.get('/book/0380795272')
        self.assertEqual(200, r.status_code)

    def test_book_post_response(self):
        r = self.app.post('/book/0380795272')
        self.assertEqual(405, r.status_code)


if __name__ == '__main__':
    unittest.main()
