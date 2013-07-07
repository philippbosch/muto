# -*- coding: utf-8 -*-
import os
from flask import Flask, abort, jsonify, redirect, request
import requests
from muto.processor import MutoProcessor


app = Flask(__name__)


@app.route('/')
def hello():
    return redirect('http://github.com/philippbosch/muto')


@app.route('/api/v1/process', methods=['POST'])
def process():
    input_data = request.json or {}

    source_url = input_data.get('source', None)
    commands = input_data.get('commands', None)

    if not source_url:
        abort(400, 'Missing "source" parameter')

    opts = {}
    if 'format' in input_data:
        opts['format'] = input_data['format']
    if 'quality' in input_data:
        opts['quality'] = input_data['quality']

    source_resp = requests.get(source_url, stream=True)
    processor = MutoProcessor(source_resp.raw)
    output_data = processor.process(commands, opts)

    return jsonify(status='ok', **output_data)


@app.errorhandler(400)
def invalid_request(error):
    return jsonify(
        status='failed', code=400, description=error.description), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
