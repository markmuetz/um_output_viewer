import os

import iris

from config import config
from setup_logging import get_logger

log = get_logger()

def convert_all():
    if not config.convert_all:
        return

    if config.delete_confim:
	if config.delete_after_convert:
	    msg_tpl = 'Convert {} to {} and delete original? y/[n]: '
	else:
	    msg_tpl = 'Convert {} to {}? y/[n]: '
	msg = msg_tpl.format(config.convert_from, config.convert_to)
	log.info(msg)
	cmd = raw_input(msg)
	log.info(cmd)
	if cmd != 'y':
	    return

    for stream, filenames in config.convert_filename_dict.items():
        if not len(filenames):
            log.warn('No files to convert for stream {}'.format(stream))
            log.warn('Have you converted them already?')
            continue

        log.info('Convert files for {}'.format(stream))
        for filename in filenames:
            pre, ext = os.path.splitext(filename)
            assert(ext[:3] == config.convert_from)
            output_filename = pre + '.' + ext[-1] + config.convert_to 

            log.info('Convert: ' + filename)
            log.info('to     : ' + output_filename)

            cubes = iris.load(filename)
            iris.save(cubes, output_filename)
	    if config.delete_after_convert:
		os.remove(filename)


if __name__ == '__main__':
    convert_all()
