import os
import datetime as dt
from collections import OrderedDict
from ConfigParser import ConfigParser
from glob import glob

class Config(ConfigParser):
    def __init__(self, filename='umov.conf'):
        ConfigParser.__init__(self)
        self.filename = filename
        self.read_config(filename)

    def read_config(self, filename):
        # print('reading config')
        self.read(filename)

        for option in self.options('settings'):
            if option[:5] == 'bool_':
                setattr(self, option[5:], self.getboolean('settings', option))
            elif option[:4] == 'int_':
                setattr(self, option[4:], self.getint('settings', option))
            elif option[-4:] == '_dir':
                setattr(self, option, os.path.expandvars(self.get('settings', option)))
            else:
                setattr(self, option, self.get('settings', option))

        file_globs = OrderedDict()
        for opt in self.options('streams'):
            file_globs[opt] = os.path.join(self.work_dir, self.get('streams', opt))

        self.filename_dict = OrderedDict()
        for opt, file_glob in file_globs.items():
            self.filename_dict[opt] = sorted(glob(file_glob))

	timestamp = dt.datetime.now().strftime(self.output_time_fmt)
        self.output_dir = os.path.join(self.output_base_dir, timestamp)

    def reload(self):
        # TODO: problematic if user has deleted an option in settings.
        self.read_config(self.filename)



config = Config()
