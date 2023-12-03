import glob
import logging
import os
from pathlib import Path
from typing import List
from random import randrange

def read_dir_content(walk_dir: str = './data/sounds', file_ext_filter: List[str] = ['.wav', '.mp3']):
    ret_val = []
    walk_dir = os.path.abspath(walk_dir)
    debug_msg = f'walk_dir (absolute) = {walk_dir} content:\n'

    for filename in glob.iglob(walk_dir + '/**/*', recursive=True):
        file_path = Path(filename)
        if file_path.is_file() and (len(file_ext_filter) == 0 or file_path.suffix in file_ext_filter):
            ret_val.append(filename)
            debug_msg += f'\t{filename}\n'

    debug_msg += f'\nTotal files with extensions {",".join(file_ext_filter)} = {len(ret_val)}'
    logging.debug(debug_msg)
    return ret_val

def get_random_file(walk_dir: str = './data/sounds', file_ext_filter: List[str] = ['.wav', '.mp3']):
    dir_content = read_dir_content(walk_dir, file_ext_filter)
    file_indx = randrange(len(dir_content))
    logging.debug(f"Random file selected {dir_content[file_indx]}")
    return dir_content[file_indx]
