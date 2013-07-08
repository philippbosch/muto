from collections import OrderedDict
import json
import requests
from .image import MutoImage


class MutoCommand:
    def __init__(self, client, name, kwargs_list):
        self.client = client
        self.name = name
        self.kwargs = OrderedDict(kwargs_list)

    def __call__(self, *args, **kwargs):
        for i in range(0, len(args)-1):
            key = self.kwargs.keys()[i]
            self.kwargs[key] = args[i]
        for key, value in kwargs.items():
            if key not in self.kwargs:
                raise TypeError("%s() got an unexpected keyword argument '%s'"
                                % self.name, key)
            self.kwargs[key] = value

        for key, value in self.kwargs.items():
            if isinstance(value, MutoRequiredArg):
                raise TypeError("%s() requires a value for argument '%s'"
                                % self.name, key)

        self.client.add_command(self.name, dict(self.kwargs))


class MutoRequiredArg:
    pass


class MutoClient:
    def __init__(self, api_endpoint):
        self.commands = []
        self.setup_commands()
        self.format = None
        self.compression_quality = None
        self.api_endpoint = api_endpoint

    def setup_commands(self):
        self.resize = MutoCommand(self, 'resize', [
            ('width', None), ('height', None), ('filter', 'undefined'),
            ('blur', 1),
        ])
        self.crop = MutoCommand(self, 'crop', [
            ('left', 0), ('top', 0), ('right', None), ('bottom', None),
            ('width', None), ('height', None), ('reset_coords', True),
        ])
        self.transform = MutoCommand(self, 'transform', [
            ('crop', ''), ('resize', ''),
        ])
        self.liquid_rescale = MutoCommand(self, 'liquid_rescale', [
            ('width', MutoRequiredArg()), ('height', MutoRequiredArg()),
            ('delta_x', 0), ('rigidity', 0),
        ])
        self.rotate = MutoCommand(self, 'rotate', [
            ('degree', MutoRequiredArg), ('background', None),
            ('reset_coords', True)
        ])
        self.flip = MutoCommand(self, 'flip', [])
        self.flop = MutoCommand(self, 'flop', [])
        self.transparentize = MutoCommand(self, 'transparency', [
            ('transparency', MutoRequiredArg),
        ])

    def from_url(self, url):
        self.source_url = url

    def add_command(self, command, kwargs):
        self.commands.append((command, kwargs))

    def process(self):
        post_data = dict(
            source=self.source_url,
            commands=self.commands,
            opts={},
        )

        if self.format is not None:
            post_data['opts']['format'] = self.format

        if self.compression_quality is not None:
            post_data['opts']['compression_quality'] = self.compression_quality

        resp = requests.post(
            '%s/process' % self.api_endpoint,
            data=json.dumps(post_data),
            headers={
                'Content-Type': 'application/json'
            }
        )
        data = resp.json()
        return MutoImage(data)
