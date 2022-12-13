# pylint: disable=C0103
""" Save remote logs path into the file.
"""
import os
import yaml
from lotr import CONFIGURATION_PATH


LOG_PATH_FILE = 'remote_logs_path.txt'


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(CONFIGURATION_PATH, 'r', encoding='utf-8') as f_conf:
        conf = yaml.safe_load(f_conf)

    logs_path = conf.get('remote_logs_path', '')
    with open(LOG_PATH_FILE, 'w', encoding='utf-8') as obj:
        obj.write(logs_path)
