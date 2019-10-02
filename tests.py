import unittest
from application import app


class ViewsTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_index_get_response(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)

    def test_index_post_response(self):
        r = self.app.post('/')
        self.assertEqual(r.status_code, 405)

    def test_login_get_response(self):
        r = self.app.get('/login')
        self.assertEqual(r.status_code, 200)

    def test_login_post_response(self):
        r = self.app.post('/login')
        self.assertEqual(r.status_code, 200)

    def test_register_get_response(self):
        r = self.app.get('/register')
        self.assertEqual(r.status_code, 200)

    def test_register_post_response(self):
        r = self.app.post('/register')
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
