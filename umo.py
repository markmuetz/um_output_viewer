import os
from glob import glob
from collections import OrderedDict
from ConfigParser import ConfigParser

import iris

from um_stash_parser.parse_stash import load_stash_vars

class UMO(object):
    def __init__(self, filename='umov.conf'):
        self.cp = ConfigParser()
        with open(filename) as f:
            self.cp.readfp(f)

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
	
	self.curr_time_index = 0


    def print_vars(self):
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

    def set_cube(self, cube_name):
	file = self.cp.get(cube_name, 'file')
	section = self.cp.getint(cube_name, 'section')
	item = self.cp.getint(cube_name, 'item')

	cube = None
	cubes = self.cube_dict[file]

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

	self.curr_cube = cube

    def next_time(self):
	self.curr_time_index += 1

    def get_curr_frame(self):
	return self.curr_cube.data[self.curr_time_index]


if __name__ == '__main__':
    umo = UMO()
    umo.print_vars()
