muto
====

A server and corresponding client library for [ImageMagick][ImageMagick]-based
image manipulation and conversion based on [Wand][Wand] for the ImageMagick
bindings, [Flask][Flask] for the web server, [Requests][Requests] for the HTTP
communication and [boto][boto] for storing the resulting images on
[Amazon S3][S3].


Concept
-------

The idea behind muto is that you have a muto server sitting somewhere on a
server in the “cloud” that does the heavy lifting, and connect to that server
from your application code through the thin muto client. You tell the client
where to get the source image from (currently that needs to be a public URL),
define some commands (e.g. resize, crop, rotate) and send it off to the server.
The server will then get the source image from the specified URL, apply the
requested commands, upload the resulting image to an S3 bucket, and return
some metadata including the URL pointing to the resulting image.


Installation
------------

You can install the package from PyPI using pip or easy_install:

    $ pip install muto

Or you can install from the latest source version:

    $ git clone git://github.com/philippbosch/muto.git
    $ cd muto/
    $ python setup.py install


Setting up a muto server
------------------------

The muto server is implemented as a [Flask Blueprint][Flask Blueprints]. In
order to setup your own server create a file called `server.py`:

```python
import os
from flask import Flask
from muto.server import muto_server

app = Flask(__name__)
app.register_blueprint(muto_server)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

Since muto server stores the resulting images in an S3 bucket it expects the
following environment variables to be set:

-   `AWS_ACCESS_KEY_ID`, get this from [Amazon Console IAM][IAM]
-   `AWS_SECRET_ACCESS_KEY`, get this from [Amazon Console IAM][IAM]
-   `AWS_STORAGE_BUCKET_NAME`, set this to the name of a bucket you created on S3

Then run the server like this:

    $ python server.py

If you want it to listen on a port other than 5000, try this:

    $ PORT=8888 python server.py


Using the muto client
---------------------

Say you have a source image at `https://muto-tests.s3.amazonaws.com/test.jpg`
that you want to resize to 960×540 and convert to a PNG.

```python
from muto.client import MutoClient

API_ENDPOINT = 'http://127.0.0.1:5000/api/v1'  # Set this to your server

client = MutoClient(API_ENDPOINT)
client.from_url('https://muto-tests.s3.amazonaws.com/test.jpg')
client.resize(960, 540)
client.format = 'png'
client.process()
print client.url  # => http://the-url-to-the-resulting-image.png
```


Supported commands and properties
---------------------------------

muto client tries to map the methods and properties exposed by [Wand][Wand] on
the [`wand.image`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html)
object as closely as possible. Currently supported:

### Properties

- [`format`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.Image.format)
- [`compression_quality`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.compression_quality)

### Methods

- [`crop(left=0, top=0, right=None, bottom=None, width=None, height=None, reset_coords=True)`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.crop)
- [`flip()`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.flip)
- [`flop()`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.flop)
- [`liquid_rescale(width, height, delta_x=0, rigidity=0)`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.liquid_rescale)
- [`resize(width=None, height=None, filter='undefined', blur=1)`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.resize)
- [`rotate(degree, background=None, reset_coords=True)`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.rotate)
- [`transform(crop='', resize='')`](http://docs.wand-py.org/en/0.3-maintenance/wand/image.html#wand.image.BaseImage.transform)

Please see the [Wand documentation](http://docs.wand-py.org/en/latest/wand/image.html)
for details.


License
-------

[MIT](http://philippbosch.mit-license.org/)


[ImageMagick]: http://imagemagick.org/
[Wand]: http://wand-py.org/
[Flask]: http://flask.pocoo.org/
[Flask Blueprints]: http://flask.pocoo.org/docs/blueprints/
[Requests]: http://python-requests.org/
[boto]: https://github.com/boto/boto
[S3]: https://aws.amazon.com/s3/
[IAM]: https://console.aws.amazon.com/iam/home#users
