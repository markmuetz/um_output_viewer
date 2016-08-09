import os

import iris

from config import config

class CubeCache(object):
    def __init__(self):
        self.tpl = '{}.nc'
        self.enabled = config.caching
        if config.caching:
            self.cache_dir = os.path.join(config.cache_dir, config.cache_name)

	    if not os.path.exists(self.cache_dir):
		os.makedirs(self.cache_dir)

    def has(self, key):
        return os.path.exists(os.path.join(self.cache_dir, self.tpl.format(key)))

    def get(self, key):
        return iris.load_cube(os.path.join(self.cache_dir, self.tpl.format(key)))

    def set(self, key, value):
        iris.save(value, os.path.join(self.cache_dir, self.tpl.format(key)))

cache = CubeCache()
