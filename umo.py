import os
from collections import OrderedDict

import iris

from config import config
from cache import cache

from um_stash_parser.parse_stash import load_stash_vars

import analysis
import output


class UMO(object):
    def __init__(self, filename='umov.conf'):
	self.curr_time_index = 0
        self.print_vars()

    def process(self):
        self.gen_output_dict()


    def print_vars(self):
        self.cube_dict = OrderedDict()
        self.stash_vars = load_stash_vars()

        for opt, filenames in config.filename_dict.items():
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

    def gen_output_dict(self):
        self.output_dict = OrderedDict()
	skip = {}

        output_vars = config.options('output_vars')
        for output_var in output_vars:
	    skip[output_var] = False

            if cache.enabled and cache.has(output_var):
                self.output_dict[output_var] = cache.get(output_var)
                skip[output_var] = True
	    else:
		self.output_dict[output_var] = []

        for opt, filenames in config.filename_dict.items():
	    for filename in filenames:
                for output_var in output_vars:
		    if skip[output_var]:
			continue
                    stream = config.get(output_var, 'stream')
		    if stream != opt:
			continue
                    section = config.getint(output_var, 'section')
                    item = config.getint(output_var, 'item')
                    analysis_fn = getattr(analysis, config.get(output_var, 'analysis'))

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
                    
                    self.output_dict[output_var].append(analysis_fn(cube))

        for output_var in output_vars:
	    if skip[output_var]:
		continue
            self.output_dict[output_var] = iris.cube.CubeList(self.output_dict[output_var]).concatenate_cube()

	    if cache.enabled:
                cache.set(output_var, self.output_dict[output_var])

    def next_time(self):
	self.curr_time_index += 1

    def get_curr_frame(self):
	return self.curr_cube.data[self.curr_time_index]


if __name__ == '__main__':
    umo = UMO()
    umo.print_vars()
