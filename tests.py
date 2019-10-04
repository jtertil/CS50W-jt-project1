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
