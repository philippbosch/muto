import os
import random
import string
import boto
from boto.s3.key import Key
from wand.image import Image


class MutoProcessor:
    def __init__(self, image_file):
        self.image_file = image_file

    def process(self, commands=None, opts=None):
        self.commands = commands
        self.opts = opts

        data = {
            'original': {},
            'result': {},
        }

        with Image(file=self.image_file) as image:
            data['original'].update(self.metadata_for_image(image))
            for command, kwargs in self.commands:
                custom_handler = getattr(self, 'handle_%s' % command, None)
                if callable(custom_handler):
                    custom_handler(image, **kwargs)
                else:
                    default_handler = getattr(image, command, None)
                    if callable(default_handler):
                        default_handler(**kwargs)
                    else:
                        raise Exception('Unknown command: %s' % command)

            if 'format' in opts:
                image.format = opts['format']

            if 'compression_quality' in opts:
                image.compression_quality = int(opts['compression_quality'])

            data['result'].update(self.metadata_for_image(image))
            key = self.store(image)
            data['result']['url'] = "http://%s/%s" % (key.bucket.name, key.key)
            data['result']['filesize'] = key.size

        return data

    def metadata_for_image(self, image):
        return dict(
            size=image.size,
            format=image.format,
            mimetype=image.mimetype,
            depth=image.depth,
            metadata=dict(image.metadata)
        )

    def store(self, image):
        s3 = boto.connect_s3()
        bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
        bucket = s3.get_bucket(bucket_name)
        key = Key(bucket)
        file_name = self.get_result_filename(image)
        key.key = "%s.%s" % (file_name, image.format.lower())
        blob = image.make_blob()
        key.set_contents_from_string(
            blob,
            headers={
                'Content-Type': image.mimetype,
            }
        )
        key.make_public()
        return key

    def get_result_filename(self, image):
        return ''.join(random.choice(
            string.ascii_letters + string.digits) for x in range(32))
