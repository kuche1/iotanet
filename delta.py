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

# TODO use these
QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY = b'0'
QUERY_TYPE_PING = b'1'

def handle_folder(path:str) -> None:

    query = util.file_read_bytes(f'{path}/query')
    sym_key = util.file_read_bytes(f'{path}/sym_key')
    sym_iv = util.file_read_bytes(f'{path}/sym_iv')
    ip = util.file_read_str(f'{path}/ip')
    port = util.file_read_int_positive_or_0(f'{path}/port')
    query_id = util.file_read_bytes(f'{path}/id')
    return_path = util.file_read_bytes(f'{path}/return_path')

    resp_header = MESSAGE_TYPE_RESPONSE + str(len(query_id)).encode() + SEP + query_id

    assert len(query) > 0

    query_type = query[0:1]
    query = query[1:]

    if query_type == QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY:

        raise NotImplemented
    
    elif query_type == QUERY_TYPE_PING:

        resp = b'yes, I got your request: ' + query

        print()
        print(f'response to ping: {resp!r}')

    else:

        assert False, f'unknown query type {query_type!r}'

    resp = resp_header + resp
    resp = encrypt_symetric(resp, sym_key, sym_iv)
    resp = return_path + resp

    create_send_entry(ip, port, resp)

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
