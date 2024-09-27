#! /usr/bin/env python3

import time
import argparse
import os
from typing import Callable

import util
from util import echo as print

from a_send_1way import ITER_SLEEP_SEC
from c_circular import FOLDER_REQUESTS, MESSAGE_TYPE_RESPONSE, SEP, FILENAME_ADDR
from j_lib_query import answer_to_query

HERE = os.path.dirname(os.path.realpath(__file__))

######
###### receive and answer to query: handle folder
######

def receive_answer_query_handle_folder(path:str) -> None:

    query = util.file_read_bytes(f'{path}/query')
    sym_key = util.file_read_symetric_key(f'{path}/sym_key')
    addr = util.file_read_addr(f'{path}/{FILENAME_ADDR}')
    query_id = util.file_read_bytes(f'{path}/id')
    return_path = util.file_read_bytes(f'{path}/return_path')

    resp_header = MESSAGE_TYPE_RESPONSE + str(len(query_id)).encode() + SEP + query_id

    assert len(query) > 0

    query_type = query[0:1]
    query = query[1:]

    answer_to_query(query_type, query, sym_key, addr, query_id, return_path, resp_header)

######
###### receive and answer to query: main
######

def receive_answer_query_main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, request_folders, _files in os.walk(FOLDER_REQUESTS):

            for request_folder in request_folders:

                path = f'{FOLDER_REQUESTS}/{request_folder}'

                util.try_finally(
                    lambda: receive_answer_query_handle_folder(path),
                    lambda: util.rmtree(path),
                )

            break

######
###### __main__
######

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: query handler')
    args = parser.parse_args()
    receive_answer_query_main()
