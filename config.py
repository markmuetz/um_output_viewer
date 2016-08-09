import os
from collections import OrderedDict
from ConfigParser import ConfigParser
from glob import glob

class Config(ConfigParser):
    def __init__(self, filename='umov.conf'):
        ConfigParser.__init__(self)
        self.filename = filename
        self.read_config(filename)

    def read_config(self, filename):
        print('reading config')
        self.read(filename)

        for option in self.options('settings'):
            if option[:5] == 'bool_':
                setattr(self, option[5:], self.getboolean('settings', option))
            elif option[:4] == 'int':
                setattr(self, option[4:], self.getint('settings', option))
            else:
                setattr(self, option, self.get('settings', option))

        file_globs = OrderedDict()
        for opt in self.options('streams'):
            file_globs[opt] = os.path.join(self.work_dir, self.get('streams', opt))

        self.filename_dict = OrderedDict()
        for opt, file_glob in file_globs.items():
            self.filename_dict[opt] = sorted(glob(file_glob))


config = Config()
