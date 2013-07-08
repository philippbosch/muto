try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import unittest
import magic
from PIL import Image
import requests
import server
from muto import MutoClient, MutoImage


class MutoTestCaseBase(unittest.TestCase):
    TEST_IMAGES = [
        'https://muto-tests.s3.amazonaws.com/01.png',
        'https://muto-tests.s3.amazonaws.com/02.jpg',
    ]

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def get_pil_image(self, url):
        resp = requests.get(url)
        img = Image.open(StringIO(resp.content))
        return img

    def get_muto_client(self):
        return MutoClient('http://localhost:5000/api/v1')


class MutoTestCase(MutoTestCaseBase):
    def test_noop_processing_from_url(self):
        client = self.get_muto_client()
        source_url = self.TEST_IMAGES[1]
        client.from_url(source_url)
        muto_image = client.process()
        self.assertIsInstance(muto_image, MutoImage)
        assert muto_image.url.startswith('http')

    def test_resize_width_and_height(self):
        client = self.get_muto_client()
        w, h = 200, 100
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.resize(width=w, height=h)
        muto_image = client.process()
        self.assertEqual(muto_image.data['result']['size'][0], w)
        self.assertEqual(muto_image.data['result']['size'][1], h)
        pil_image = self.get_pil_image(muto_image.url)
        self.assertEqual(pil_image.size[0], w)
        self.assertEqual(pil_image.size[1], h)

    def test_resize_width_only(self):
        client = self.get_muto_client()
        w = 200
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.resize(width=w)
        muto_image = client.process()
        original = muto_image.data['original']['size']
        result = muto_image.data['result']['size']
        self.assertEqual(result[0], w)
        self.assertEqual(result[1], original[1])
        pil_image = self.get_pil_image(muto_image.url)
        self.assertEqual(pil_image.size[0], w)
        self.assertEqual(pil_image.size[1], original[1])

    def test_resize_height_only(self):
        client = self.get_muto_client()
        h = 200
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.resize(height=h)
        muto_image = client.process()
        original = muto_image.data['original']['size']
        result = muto_image.data['result']['size']
        self.assertEqual(result[0], original[0])
        self.assertEqual(result[1], h)
        pil_image = self.get_pil_image(muto_image.url)
        self.assertEqual(pil_image.size[0], original[0])
        self.assertEqual(pil_image.size[1], h)

    def test_transform_resize(self):
        client = self.get_muto_client()
        w, h = 160, 160
        geometry = '%dx%d' % (w, h)
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.transform(resize=geometry)
        muto_image = client.process()
        result = muto_image.data['result']['size']
        self.assertLessEqual(result[0], w)
        self.assertLessEqual(result[1], h)
        pil_image = self.get_pil_image(muto_image.url)
        self.assertLessEqual(pil_image.size[0], w)
        self.assertLessEqual(pil_image.size[1], h)

    def test_transform_resize_width_only(self):
        client = self.get_muto_client()
        w = 160
        geometry = '%dx' % w
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.transform(resize=geometry)
        muto_image = client.process()
        original = muto_image.data['original']['size']
        result = muto_image.data['result']['size']
        expected_height = round(original[1] * result[0]/float(original[0]))
        self.assertEqual(result[0], w)
        self.assertEqual(result[1], expected_height)
        pil_image = self.get_pil_image(muto_image.url)
        self.assertEqual(pil_image.size[0], w)
        self.assertEqual(result[1], expected_height)

    def test_transform_resize_height_only(self):
        client = self.get_muto_client()
        h = 160
        geometry = 'x%d' % h
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.transform(resize=geometry)
        muto_image = client.process()
        original = muto_image.data['original']['size']
        result = muto_image.data['result']['size']
        expected_width = round(original[0] * result[1]/float(original[1]))
        self.assertEqual(result[1], h)
        self.assertEqual(result[0], expected_width)
        pil_image = self.get_pil_image(muto_image.url)
        self.assertEqual(result[1], h)
        self.assertEqual(pil_image.size[0], expected_width)

    def test_quality(self):
        client = self.get_muto_client()
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)
        client.format = 'jpg'

        client.compression_quality = 100
        high = client.process()

        client.compression_quality = 1
        low = client.process()

        ratio = high.data['result']['filesize']/low.data['result']['filesize']
        self.assertGreater(ratio, 10)

    def test_format(self):
        client = self.get_muto_client()
        source_url = self.TEST_IMAGES[0]
        client.from_url(source_url)

        client.format = 'jpg'
        img_jpg = client.process()
        img_jpg_mime = magic.from_buffer(img_jpg.read(), mime=True)
        self.assertEqual(img_jpg_mime, 'image/jpeg')

        client.format = 'gif'
        img_gif = client.process()
        img_gif_mime = magic.from_buffer(img_gif.read(), mime=True)
        self.assertEqual(img_gif_mime, 'image/gif')


class MutoTinkerTestCase(MutoTestCaseBase):
    pass

if __name__ == '__main__':
    unittest.main(defaultTest='MutoTestCase')
