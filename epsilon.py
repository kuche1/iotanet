#! /usr/bin/env python3

# TODO
#
# this can crash
#
# same as the others, do the threading thing

import argparse
import time
import os
import shutil

from alpha import ITER_SLEEP_SEC
from gamma import FOLDER_RESPONSES
from delta import read_file_bytes

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        response_folders:list[str] = []
        for _path, response_folders, _files in os.walk(FOLDER_RESPONSES):
            break
        
        for response_folder in response_folders:

            path = f'{FOLDER_RESPONSES}/{response_folder}'

            query_id = read_file_bytes(f'{path}/id')
            response = read_file_bytes(f'{path}/response')

            print()
            print(f'{query_id=}')
            print(f'{response=}')

            shutil.rmtree(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: response evaluator')
    args = parser.parse_args()
    main()
