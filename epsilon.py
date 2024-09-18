#! /usr/bin/env python3

import argparse
import time
import os
import shutil

import util

from alpha import ITER_SLEEP_SEC
from beta import Node
from gamma import FOLDER_RESPONSES, FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, send_circular, FILENAME_SENDER_ADDR

def send_query(query_type:bytes, query_args:bytes, private_data:bytes, path_to_dest:list[Node], path_way_back:list[Node]) -> None:

    assert len(query_type) == 1

    query = query_type + query_args

    private_data = query_type + private_data

    send_circular(
        query,
        private_data,
        path_to_dest,
        path_way_back,
    )

def handle_folder(path:str) -> None:

    sender_addr = util.file_read_addr(f'{path}/{FILENAME_SENDER_ADDR}')
    private_data = util.file_read_bytes(f'{path}/{FILENAME_PRIVATE_DATA}')
    response = util.file_read_bytes(f'{path}/{FILENAME_RESPONSE}')

    assert len(private_data) > 0

    query_type = private_data[0:1]
    private_data = private_data[1:]

    print()
    print(f'{sender_addr=}')
    print(f'{query_type=}')
    print(f'{response=}')
    print(f'{private_data=}')

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
    parser = argparse.ArgumentParser('daemon: query response evaluator')
    args = parser.parse_args()
    main()
