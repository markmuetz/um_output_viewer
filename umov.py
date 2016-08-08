import os
from glob import glob
from collections import OrderedDict
from ConfigParser import ConfigParser
import hashlib
from subprocess import check_output
import datetime as dt
import shutil

import iris

from um_stash_parser.parse_stash import load_stash_vars
import analysis
import output

class UMOV(object):
    def __init__(self, filename='umov.conf'):
        self.read_config(filename)


    def run(self):
        if self.cp.getboolean('settings', 'process'):
            self.process()
        if self.cp.getboolean('settings', 'output'):
            self.output()


    def process(self):
        print('processing')
        self.get_vars()


    def output(self):
        print('outputting')
        self.gen_output_dict()
        self.gen_output()


    def read_config(self, filename):
        self.githash = check_output('git rev-parse HEAD'.split()).strip()
        self.gitstatus = check_output('git status --porcelain'.split())
        self.local_changes = False if self.gitstatus == '' else True

        self.cp = ConfigParser()
        with open(filename) as f:
            self.cp.readfp(f)
            f.seek(0)
            lines = f.readlines()
            self.cache_hash = hashlib.sha1(''.join(lines) + self.githash).hexdigest()

        self.work_dir = self.cp.get('paths', 'work_dir')

        file_globs = OrderedDict()
        for opt in self.cp.options('files'):
            file_globs[opt] = os.path.join(self.work_dir, self.cp.get('files', opt))

        self.filename_dict = OrderedDict()
        for opt, file_glob in file_globs.items():
            self.filename_dict[opt] = sorted(glob(file_glob))

        if self.cp.getboolean('settings', 'ignore_orography_warnings'):
            # DO NOT LEAVE IN!!!
            # Added so as orography warning not shown on iris.load.
            import warnings
            warnings.filterwarnings("ignore")


    def get_vars(self):
        self.cube_dict = OrderedDict()
        self.stash_vars = load_stash_vars()

        for opt, filenames in self.filename_dict.items():
            print(opt)
            cubes = iris.load(filenames[0])
            self.cube_dict[opt] = cubes
            for cube in cubes:
                cube_stash = cube.attributes['STASH']
                section, item = cube_stash.section, cube_stash.item
                stash_name = self.stash_vars[section][item]
                print('{0:>4}{1:>4} {2} {3}'.format(section, item, stash_name, cube.shape))


    def gen_output_dict(self):
        if self.cp.getboolean('settings', 'caching'):
            cache_dir = os.path.join(self.cp.get('paths', 'cache_dir'),
                                     self.cache_hash)

        self.output_dict = OrderedDict()

        for output_var in self.cp.options('output_vars'):
            self.output_dict[output_var] = []

        for opt, filenames in self.filename_dict.items():
            for filename in filenames[:5]:
                for output_var in self.cp.options('output_vars'):

                    file = self.cp.get(output_var, 'file')
                    section = self.cp.getint(output_var, 'section')
                    item = self.cp.getint(output_var, 'item')
                    analysis_fn = getattr(analysis, self.cp.get(output_var, 'analysis'))

                    cubes = iris.load(filename)
                    cube = None

                    for test_cube in cubes:
                        cube_stash = test_cube.attributes['STASH']
                        cube_section, cube_item = cube_stash.section, cube_stash.item
                        if cube_section == section and cube_item == item:
                            print('Found cube {0:>3} {1:>3}'.format(section, item))
                            if cube != None:
                                print('Found duplicates')
                            cube = test_cube

                    if not cube:
                        raise Exception('Cannot find cube {}'.format(output_var))
                    
                    self.output_dict[output_var].extend(analysis_fn(cube))


    def gen_output(self):
	timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M')
        output_dir = os.path.join(self.cp.get('paths', 'output_dir'), timestamp)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
	
	shutil.copy('umov.conf', output_dir)

        for output_fn_name in self.cp.options('outputs'):
            variables = self.cp.get(output_fn_name, 'variables')
            output_vars_for_fn = map(str.strip, variables.split(','))
            output_dict_for_fn = OrderedDict()

            for output_var in output_vars_for_fn:
                output_dict_for_fn[output_var] = self.output_dict[output_var]

            output_fn = getattr(output, output_fn_name)
            full_path = os.path.join(output_dir,
                                     self.cp.get(output_fn_name, 'filename') + '.png')

            output_fn(output_dict_for_fn.items(), full_path)


if __name__ == '__main__':
    umov = UMOV()
    umov.run()
