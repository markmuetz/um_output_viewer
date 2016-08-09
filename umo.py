import os
from collections import OrderedDict

import iris

from config import config
from cache import cache
from setup_logging import get_logger

from um_stash_parser.parse_stash import load_stash_vars

import analysis
import output

log = get_logger()

class UMO(object):
    def __init__(self, filename='umov.conf'):
	self.curr_time_index = 0
	self.curr_level_index = 0
        self.all_cubes = []
        self.print_vars()

    def process(self):
        self.gen_output_dict()


    def print_vars(self):
        self.cube_dict = OrderedDict()
        self.stash_vars = load_stash_vars()

        for opt, filenames in config.filename_dict.items():
            log.info(opt)
            cubes = iris.load(filenames[0])
            self.cube_dict[opt] = cubes
            for cube in cubes:
                self.all_cubes.append(cube)
                cube_stash = cube.attributes['STASH']
                section, item = cube_stash.section, cube_stash.item
                stash_name = self.stash_vars[section][item]
                log.info('{0:>4}{1:>4} {2} {3}'.format(section, item, stash_name, cube.shape))

    def set_cube(self, cube_name):
	stream = config.get(cube_name, 'stream')
	section = config.getint(cube_name, 'section')
	item = config.getint(cube_name, 'item')

	cube = None
	cubes = self.cube_dict[stream]

	for test_cube in cubes:
	    cube_stash = test_cube.attributes['STASH']
	    cube_section, cube_item = cube_stash.section, cube_stash.item
	    if cube_section == section and cube_item == item:
		log.debug('Found cube {0:>3} {1:>3}'.format(section, item))
		if cube != None:
		    log.info('Found duplicates')
		cube = test_cube

	if not cube:
	    raise Exception('Cannot find cube {}'.format(output_var))

	self.curr_cube = cube
        self.curr_cube_index = self.all_cubes.index(self.curr_cube)

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
                            log.debug('Found cube {0:>3} {1:>3}'.format(section, item))
                            if cube != None:
                                log.info('Found duplicates')
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

    def prev_time(self):
	self.curr_time_index -= 1
        self.check_indices_in_range()

    def next_time(self):
	self.curr_time_index += 1
        self.check_indices_in_range()

    def prev_level(self):
	self.curr_level_index -= 1
        self.check_indices_in_range()

    def next_level(self):
	self.curr_level_index += 1
        self.check_indices_in_range()

    def prev_cube(self):
	self.curr_cube_index -= 1
        self.curr_cube_index %= len(self.all_cubes)
        self.curr_cube = self.all_cubes[self.curr_cube_index]
        self.check_indices_in_range()

    def next_cube(self):
	self.curr_cube_index += 1
        self.curr_cube_index %= len(self.all_cubes)
        self.curr_cube = self.all_cubes[self.curr_cube_index]
        self.check_indices_in_range()

    def check_indices_in_range(self):
        self.curr_time_index %= self.curr_cube.shape[0]
        if self.curr_cube.ndim == 4:
            self.curr_level_index %= self.curr_cube.shape[1]

    def get_curr_2d_slice(self):
        if self.curr_cube.ndim == 3:
            return self.curr_cube[self.curr_time_index]
        elif self.curr_cube.ndim == 4:
            return self.curr_cube[self.curr_time_index, self.curr_level_index]


if __name__ == '__main__':
    umo = UMO()
    umo.print_vars()
