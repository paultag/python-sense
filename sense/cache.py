import os
import json


class Cache(object):
    """
    Filesystem based "cache", writes JSON files in the clear to disk.

    Key names are interpolated directly into the path, do not allow user
    input to dictate the key you're reading from.
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.expanduser("~/.sense/")

        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _path(self, name):
        return os.path.join(self.base_dir, name)

    def _exists(self, name):
        return os.path.exists(self._path(name))

    def get(self, name, default=None):
        try:
            return self.load(name)
        except KeyError:
            return default

    def load(self, name):
        if not self._exists(name):
            raise KeyError(name)
        with open(self._path(name)) as fd:
            return json.load(fd)

    def write(self, name, data):
        with open(self._path(name), 'w') as fd:
            return json.dump(data, fd)
