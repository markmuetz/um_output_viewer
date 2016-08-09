import os
import datetime as dt
from collections import OrderedDict
import shutil

import pylab as plt

from config import config
from local_state import state
from setup_logging import get_logger

from umo import UMO
import output

log = get_logger()

def main():
    log.info('Running main')
    if config.ignore_orography_warnings:
        # DO NOT LEAVE IN!!!
        # Added so as orography warning not shown on iris.load.
        log.warn('Disabling warnings')
        import warnings
        warnings.filterwarnings("ignore")

    umo = UMO()
    umov = UMOV(umo)
    umov.run()
    return umov

class UMOV(object):
    def __init__(self, umo):
        self.umo = umo


    def run(self):
        if config.process:
            self.process()
        if config.output:
            self.output()


    def process(self):
        log.info('processing')
        self.umo.process()


    def output(self):
        log.info('outputting')
        self.gen_output()


    def print_streams(self):
        for stream in config.options('streams'):
            print(stream)

    def print_stream_files(self, stream):
        for filename in config.filename_dict[stream]:
            print(filename)

    def print_all_files(self):
        for stream in config.options('streams'):
            print(stream)
            for filename in config.filename_dict[stream]:
                print('  ' + filename)


    def gen_output(self):
        output_dir = config.output_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
	
	shutil.copy('umov.conf', output_dir)

        for output_fn_name in config.options('output_fn_names'):
            log.debug(output_fn_name)
            variables = config.get(output_fn_name, 'variables')
            output_vars_for_fn = map(str.strip, variables.split(','))
            output_dict_for_fn = OrderedDict()

            for output_var in output_vars_for_fn:
                output_dict_for_fn[output_var] = self.umo.output_dict[output_var]

            output_fn = getattr(output, output_fn_name)
            full_path = os.path.join(output_dir,
                                     config.get(output_fn_name, 'filename') + '.png')

            output_fn(output_dict_for_fn.items(), full_path)

    def display_curr_frame(self):
        plt.ion()
        plt.clf()
        self.frame = self.umo.get_curr_2d_slice()
        time_since_1970 = dt.timedelta(hours=self.frame.coord('time').points[0])
        frame_time = dt.datetime(1970, 1, 1) + time_since_1970
        fmt = '%Y-%m-%d %H:%M'
	timestamp = frame_time.strftime(fmt)

        plt.title(timestamp)
        plt.imshow(self.frame.data, origin='lower', interpolation='nearest')

    def play_frames(self):
        self.umo.curr_time_index = 0
        for i in range(self.umo.curr_cube.shape[0]):
            self.display_curr_frame()
            self.umo.next_time()
            plt.pause(0.1)

    def play_vertical_frames(self):
        assert(self.umo.curr_cube.ndim == 4)
        self.umo.curr_level = 0
        for i in range(self.umo.curr_cube.shape[1]):
            self.display_curr_frame()
            self.umo.next_level()
            plt.pause(0.1)


if __name__ == '__main__':
    umov = main()
