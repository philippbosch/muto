# -*- coding: utf-8 -*-
import os
from flask import Flask
from muto.server import muto_server


app = Flask(__name__)
app.register_blueprint(muto_server)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
