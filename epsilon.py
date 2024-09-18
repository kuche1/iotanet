#! /usr/bin/env python3

import argparse
import time
import os
import shutil

from alpha import ITER_SLEEP_SEC
from gamma import FOLDER_RESPONSES
from delta import read_file_bytes, try_finally

def handle_folder(path:str) -> None:

    query_id = read_file_bytes(f'{path}/id')
    response = read_file_bytes(f'{path}/response')

    print()
    print(f'{query_id=}')
    print(f'{response=}')

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, response_folders, _files in os.walk(FOLDER_RESPONSES):

            for response_folder in response_folders:

                path = f'{FOLDER_RESPONSES}/{response_folder}'

                try_finally(
                    lambda: handle_folder(path),
                    lambda: shutil.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: response evaluator')
    args = parser.parse_args()
    main()
