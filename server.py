# -*- coding: utf-8 -*-
import os
from flask import Flask, abort, jsonify, request
import requests
from wand.image import Image


app = Flask(__name__)


class MutoProcessor:
    target_format = 'jpg'

    def __init__(self, image_file):
        self.image_file = image_file

    def process(self, commands={}, format=None, quality=None):
        data = {
            'original': {},
            'result': {},
        }
        with Image(file=self.image_file) as img:
            data['original'].update(self.metadata_for_image(img))
            for command in commands:
                handler = getattr(self, 'handle_%s' % command, None)
                if callable(handler):
                    handler(img, commands[command])
                else:
                    raise Exception('Unknown command: %s' % command)

            if format:
                img.format = format

            if quality:
                img.compression_quality = quality

            data['result'].update(self.metadata_for_image(img))
        return data

    def handle_resize(self, image, size):
        w, h = size.split('x')
        image.resize(int(w), int(h))

    def handle_crop(self, image, crop):
        raise NotImplemented

    def handle_transform(self, image, transform):
        raise NotImplemented

    def handle_liquid_rescale(self, image, size):
        w, h = size.split('x')
        image.liquid_rescale(int(w), int(h))

    def handle_rotate(self, image, degrees):
        image.rotate(int(degrees))

    def handle_flip(self, image):
        image.flip()

    def handle_flop(self, image):
        image.flop()

    def metadata_for_image(self, image):
        return dict(
            size=image.size,
            format=image.format,
            mimetype=image.mimetype,
            depth=image.depth,
            metadata=dict(image.metadata)
        )


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/api/v1/process', methods=['POST'])
def process():
    input_data = request.json or {}

    source_url = input_data.get('source', None)
    commands = input_data.get('commands', {})
    format = input_data.get('format', None)
    quality = input_data.get('quality', None)

    if not source_url:
        abort(400, 'Missing "source" parameter')

    source_resp = requests.get(source_url, stream=True)
    processor = MutoProcessor(source_resp.raw)
    output_data = processor.process(commands, format=format, quality=quality)

    return jsonify(status='ok', **output_data)


@app.errorhandler(400)
def invalid_request(error):
    return jsonify(
        status='failed', code=400, description=error.description), 400


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
