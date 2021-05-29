""" Save remote logs path into the file.
"""
import os
import yaml
from lotr import CONFIGURATION_PATH


LOG_PATH_FILE = 'remote_logs_path'


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    log_path = conf.get('remote_logs_path', '')
    with open(LOG_PATH_FILE, 'w') as obj:
        obj.write(log_path)
