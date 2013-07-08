# -*- coding: utf-8 -*-
from flask import abort, Blueprint, jsonify, request
import requests
from .processor import MutoProcessor


muto_server = Blueprint('muto_server', __name__)


@muto_server.route('/api/v1/process', methods=['POST'])
def process():
    input_data = request.json or {}

    source_url = input_data.get('source', None)
    commands = input_data.get('commands', None)

    if not source_url:
        abort(400, 'Missing "source" parameter')

    opts = {}
    if 'format' in input_data['opts']:
        opts['format'] = input_data['opts']['format']
    if 'compression_quality' in input_data['opts']:
        opts['compression_quality'] = input_data['opts']['compression_quality']

    source_resp = requests.get(source_url, stream=True)
    processor = MutoProcessor(source_resp.raw)
    output_data = processor.process(commands, opts)

    return jsonify(status='ok', **output_data)


@muto_server.errorhandler(400)
def invalid_request(error):
    return jsonify(
        status='failed', code=400, description=error.description), 400
