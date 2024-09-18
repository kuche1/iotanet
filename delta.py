#! /usr/bin/env python3

# TODO this can crash
# perhaps it's best to just do the threaded shit

import time
import argparse
import os
import shutil

from alpha import ITER_SLEEP_SEC, create_send_entry
from beta import encrypt_symetric
from gamma import FOLDER_REQUESTS, TYPE_RESPONSE, SEP

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

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        request_folders:list[str] = []
        for _path, request_folders, _files in os.walk(FOLDER_REQUESTS):
            break
        
        for request_folder in request_folders:

            path = f'{FOLDER_REQUESTS}/{request_folder}'

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

            shutil.rmtree(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: request handler')
    args = parser.parse_args()
    main()
