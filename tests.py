import unittest
from flask import json
import server


class MutoTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def api_url(self, path):
        return '/api/v1' + path

    def test_hello(self):
        resp = self.app.get('/')
        assert 'Hello' in resp.data

    def test_missing_any_parameters(self):
        resp = self.app.post(self.api_url('/process'))
        data = json.loads(resp.data)
        assert data['status'] == 'failed'

    def test_basic_image_processing_from_url(self):
        source_url = 'https://muto-tests.s3.amazonaws.com/02.jpg'
        post_data = dict(
            source=source_url,
            commands=dict(
                resize='640x480',
            ),
            format='jpg'
        )
        resp = self.app.post(
            self.api_url('/process'), data=json.dumps(post_data),
            content_type='application/json')
        data = json.loads(resp.data)
        assert data['status'] == 'ok'

if __name__ == '__main__':
    unittest.main()
