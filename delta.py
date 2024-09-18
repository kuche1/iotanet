#! /usr/bin/env python3

import time
import argparse
import os
import shutil
from typing import Callable

from alpha import ITER_SLEEP_SEC, create_send_entry
from beta import encrypt_symetric
from gamma import FOLDER_REQUESTS, TYPE_RESPONSE, SEP

######
###### generic: file read
######

def read_file_bytes(file:str) -> bytes:
    with open(file, 'rb') as f:
        return f.read()

def read_file_str(file:str) -> str:
    with open(file, 'r') as f:
        return f.read()

def read_file_int_positive_or_0(file:str) -> int:
    data = read_file_str(file)
    num = int(data)
    assert num >= 0
    return num

######
###### generic: try_finally
######

def try_finally(fnc:Callable[[],None], cleanup:Callable[[],None]) -> None:
    # TODO we could add some fancy formating, along with timestamp in case of errors
    try:
        fnc()
    finally:
        cleanup()

######
###### ...
######

def handle_folder(path:str) -> None:

    query = read_file_bytes(f'{path}/query')
    sym_key = read_file_bytes(f'{path}/sym_key')
    sym_iv = read_file_bytes(f'{path}/sym_iv')
    ip = read_file_str(f'{path}/ip')
    port = read_file_int_positive_or_0(f'{path}/port')
    query_id = read_file_bytes(f'{path}/id')
    return_path = read_file_bytes(f'{path}/return_path')

    print()

    resp = b'yes, I got your request: ' + query
    print(f'{resp=}')

    resp = TYPE_RESPONSE + str(len(query_id)).encode() + SEP + query_id + resp
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

                try_finally(
                    lambda: handle_folder(path),
                    lambda: shutil.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: request handler')
    args = parser.parse_args()
    main()
