# -*- coding: utf-8 -*-
import os
import random
import string
import boto
from boto.s3.key import Key
from flask import Flask, abort, jsonify, request
import requests
from wand.color import Color
from wand.image import Image


app = Flask(__name__)


class MutoProcessor:
    target_format = 'jpg'

    def __init__(self, image_file):
        self.image_file = image_file

    def process(self, commands={}, opts={}):
        self.commands = commands
        self.opts = opts

        data = {
            'original': {},
            'result': {},
        }
        with Image(file=self.image_file) as image:
            data['original'].update(self.metadata_for_image(image))

            for command in self.commands:
                handler = getattr(self, 'handle_%s' % command, None)
                if callable(handler):
                    handler(image, self.commands[command])
                else:
                    raise Exception('Unknown command: %s' % command)

            if 'format' in opts:
                image.format = opts['format']

            if 'quality' in opts:
                image.compression_quality = int(opts['quality'])

            data['result'].update(self.metadata_for_image(image))
            data['result']['url'] = self.store(image)

        return data

    def handle_resize(self, image, size):
        if isinstance(size, str) or isinstance(size, unicode):
            size = size.split('x')
        if isinstance(size, list):
            w, h = size
        elif isinstance(size, dict):
            w, h = size['width'], size['height']
        image.resize(int(w), int(h))

    def handle_crop(self, image, crop):
        if isinstance(crop, str) or isinstance(crop, unicode):
            crop = crop.split(',')
        if isinstance(crop, list):
            left, top, right, bottom = crop
            kwargs = {
                'left': int(left),
                'top': int(top),
                'right': int(right),
                'bottom': int(bottom)
            }
        elif isinstance(crop, dict):
            kwargs = crop
        image.crop(**kwargs)

    def handle_transform(self, image, transform):
        raise NotImplemented

    def handle_liquid_rescale(self, image, size):
        if isinstance(size, str) or isinstance(size, unicode):
            size = size.split('x')
        if isinstance(size, list):
            w, h = size
        elif isinstance(size, dict):
            w, h = size['width'], size['height']
        image.liquid_rescale(int(w), int(h))

    def handle_rotate(self, image, degrees):
        image.rotate(int(degrees))

    def handle_flip(self, image, flip):
        if flip:
            image.flip()

    def handle_flop(self, image, flop):
        if flop:
            image.flop()

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
        bucket_name = 'img.muto.syntop.io'
        bucket = s3.get_bucket(bucket_name)
        key = Key(bucket)
        file_name = self.get_result_filename(image)
        key.key = "%s.%s" % (file_name, image.format.lower())
        key.set_contents_from_string(
            image.make_blob(),
            headers={
                'Content-Type': image.mimetype,
            }
        )
        key.make_public()
        return "http://%s/%s" % (key.bucket.name, key.key)

    def get_result_filename(self, image):
        return ''.join(random.choice(
            string.ascii_letters + string.digits) for x in range(32))


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/api/v1/process', methods=['POST'])
def process():
    input_data = request.json or {}

    source_url = input_data.get('source', None)
    commands = input_data.get('commands', {})

    opts = {}
    if 'format' in input_data:
        opts['format'] = input_data['format']
    if 'quality' in input_data:
        opts['quality'] = input_data['quality']
    if 'background_color' in input_data:
        opts['background_color'] = input_data['background_color']

    if not source_url:
        abort(400, 'Missing "source" parameter')

    source_resp = requests.get(source_url, stream=True)
    processor = MutoProcessor(source_resp.raw)
    output_data = processor.process(commands, opts)

    return jsonify(status='ok', **output_data)


@app.errorhandler(400)
def invalid_request(error):
    return jsonify(
        status='failed', code=400, description=error.description), 400


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
