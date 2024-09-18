#! /usr/bin/env python3

import time
import argparse
import os
import shutil
from typing import Callable

import util

from alpha import ITER_SLEEP_SEC, create_send_entry
from beta import encrypt_symetric
from gamma import FOLDER_REQUESTS, MESSAGE_TYPE_RESPONSE, SEP

def handle_folder(path:str) -> None:

    query = util.file_read_bytes(f'{path}/query')
    sym_key = util.file_read_bytes(f'{path}/sym_key')
    sym_iv = util.file_read_bytes(f'{path}/sym_iv')
    ip = util.file_read_str(f'{path}/ip')
    port = util.file_read_int_positive_or_0(f'{path}/port')
    query_id = util.file_read_bytes(f'{path}/id')
    return_path = util.file_read_bytes(f'{path}/return_path')

    print()

    resp = b'yes, I got your request: ' + query
    print(f'{resp=}')

    resp = MESSAGE_TYPE_RESPONSE + str(len(query_id)).encode() + SEP + query_id + resp
    print(f'{resp=}')

    resp = encrypt_symetric(resp, sym_key, sym_iv)
    print(f'{resp=}')

    payload = return_path + resp

    create_send_entry(ip, port, payload)

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, request_folders, _files in os.walk(FOLDER_REQUESTS):

            for request_folder in request_folders:

                path = f'{FOLDER_REQUESTS}/{request_folder}'

                util.try_finally(
                    lambda: handle_folder(path),
                    lambda: shutil.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: request handler')
    args = parser.parse_args()
    main()
