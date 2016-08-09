import os
from collections import OrderedDict
import datetime as dt
import shutil

from config import config
from local_state import state

from umo import UMO
import output

def main():
    if config.ignore_orography_warnings:
        # DO NOT LEAVE IN!!!
        # Added so as orography warning not shown on iris.load.
        import warnings
        warnings.filterwarnings("ignore")

    umo = UMO()
    umov = UMOV(umo)
    umov.run()

class UMOV(object):
    def __init__(self, umo):
        self.umo = umo


    def run(self):
        if config.process:
            self.process()
        if config.output:
            self.output()


    def process(self):
        print('processing')
        self.umo.process()


    def output(self):
        print('outputting')
        self.gen_output()


    def gen_output(self):
	timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M')
        output_dir = os.path.join(config.output_dir, timestamp)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
	
	shutil.copy('umov.conf', output_dir)

        for output_fn_name in config.options('output_fn_names'):
            print(output_fn_name)
            variables = config.get(output_fn_name, 'variables')
            output_vars_for_fn = map(str.strip, variables.split(','))
            output_dict_for_fn = OrderedDict()

            for output_var in output_vars_for_fn:
                output_dict_for_fn[output_var] = self.umo.output_dict[output_var]

            output_fn = getattr(output, output_fn_name)
            full_path = os.path.join(output_dir,
                                     config.get(output_fn_name, 'filename') + '.png')

            output_fn(output_dict_for_fn.items(), full_path)


if __name__ == '__main__':
    main()
