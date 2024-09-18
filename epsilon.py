#! /usr/bin/env python3

import argparse
import time
import os
import shutil

import util

from alpha import ITER_SLEEP_SEC
from gamma import FOLDER_RESPONSES

def handle_folder(path:str) -> None:

    query_id = util.file_read_bytes(f'{path}/encrypted_id')
    response = util.file_read_bytes(f'{path}/response')

    print()
    print(f'{query_id=}')
    print(f'{response=}')

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, response_folders, _files in os.walk(FOLDER_RESPONSES):

            for response_folder in response_folders:

                path = f'{FOLDER_RESPONSES}/{response_folder}'

                util.try_finally(
                    lambda: handle_folder(path),
                    lambda: shutil.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: response evaluator')
    args = parser.parse_args()
    main()
