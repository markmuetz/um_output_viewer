from subprocess import check_output
import hashlib

from config import config

class LocalState(object):
    def __init__(self):
        self.githash = check_output('git rev-parse HEAD'.split()).strip()
        self.gitstatus = check_output('git status --porcelain'.split())
        self.local_changes = False if self.gitstatus == '' else True

        with open(config.filename) as f:
            lines = f.readlines()
            self.cache_hash = hashlib.sha1(''.join(lines)).hexdigest()

state = LocalState()
