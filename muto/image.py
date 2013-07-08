import requests


class MutoImage:
    def __init__(self, data):
        self.data = data
        self.url = data['result']['url']
        self.file = None

    def read(self, size=None):
        if self.file is None:
            resp = requests.get(self.url, stream=True)
            self.file = resp.raw
        return self.file.read(size)

    def readLine(self, size=None):
        raise NotImplemented

    def write(self, data):
        raise NotImplemented

    def close(self):
        pass
