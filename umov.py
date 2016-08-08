import os
from glob import glob
from collections import OrderedDict
from ConfigParser import ConfigParser

import iris

from um_stash_parser.parse_stash import load_stash_vars
import analysis
import output

# DO NOT LEAVE IN!!!
# Added so as orography warning not shown on iris.load.
import warnings
warnings.filterwarnings("ignore")


def read_config():
    cp = ConfigParser()
    cp.read('umov.conf')
    work_dir = cp.get('paths', 'work_dir')

    file_globs = OrderedDict()
    for opt in cp.options('files'):
        file_globs[opt] = os.path.join(work_dir, cp.get('files', opt))

    filename_dict = OrderedDict()
    for opt, file_glob in file_globs.items():
        # print(file_glob)
        filename_dict[opt] = sorted(glob(file_glob))
    return cp, filename_dict


def get_vars(filename_dict):
    cube_dict = OrderedDict()
    stash_vars = load_stash_vars()

    for opt, filenames in filename_dict.items():
        print(opt)
        cubes = iris.load(filenames[0])
        cube_dict[opt] = cubes
        for cube in cubes:
            cube_stash = cube.attributes['STASH']
            section, item = cube_stash.section, cube_stash.item
            stash_name = stash_vars[section][item]
            print('{0:>4}{1:>4} {2} {3}'.format(section, item, stash_name, cube.shape))

    return cube_dict


def gen_output(cp, filename_dict, cube_dict):
    if cp.getboolean('settings', 'caching'):
        cache_dir = cp.get('paths', 'cache_dir')

    output_dict = OrderedDict()

    for output_var in cp.options('output_vars'):
        output_dict[output_var] = []

    for opt, filenames in filename_dict.items():
        for filename in filenames[:5]:

            for output_var in cp.options('output_vars'):

                file = cp.get(output_var, 'file')
                section = cp.getint(output_var, 'section')
                item = cp.getint(output_var, 'item')
                analysis_fn = getattr(analysis, cp.get(output_var, 'analysis'))

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
                
                output_dict[output_var].extend(analysis_fn(cube))

    return output_dict


if __name__ == '__main__':
    cp, filename_dict = read_config()
    cube_dict = get_vars(filename_dict)
    output_dict = gen_output(cp, filename_dict, cube_dict)

    for output_fn_name in cp.options('outputs'):
        variables = cp.get(output_fn_name, 'variables')
        output_vars_for_fn = map(str.strip, variables.split(','))
        output_dict_for_fn = OrderedDict()
        for output_var in output_vars_for_fn:
            output_dict_for_fn[output_var] = output_dict[output_var]
        output_fn = getattr(output, output_fn_name)
        output_dir = cp.get('paths', 'output_dir')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        full_path = os.path.join(output_dir,
                                 cp.get(output_fn_name, 'filename') + '.png')

        output_fn(output_dict_for_fn.items(), full_path)
