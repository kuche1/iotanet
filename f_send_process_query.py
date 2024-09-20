#! /usr/bin/env python3

import argparse
import time
import os
import shutil
import random

import util
from util import echo as print
from util import Node, Addr

from a_send_1way import ITER_SLEEP_SEC
from c_circular import FOLDER_RESPONSES, FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, FILENAME_RESPONDER_ADDR
from d_peer import peer_increase_queries_answered, send_measure

######
###### send query
######

def send_query(query_type:bytes, query_args:bytes, private_data:bytes, dest_addr:Addr, extra_hops:int) -> None:

    assert len(query_type) == 1
    query = query_type + query_args

    private_data = query_type + private_data

    send_measure(query, private_data, dest_addr, extra_hops)

######
###### process query answer
######

def handle_folder(path:str) -> None:

    responder_addr = util.file_read_addr(f'{path}/{FILENAME_RESPONDER_ADDR}')
    private_data = util.file_read_bytes(f'{path}/{FILENAME_PRIVATE_DATA}')
    response = util.file_read_bytes(f'{path}/{FILENAME_RESPONSE}')

    assert len(private_data) > 0

    # TODO this shouldn't be happening here (1 it should be in a "peer" folder ) (2 it should be in it's own thread, so that there is no change the multiple processess call in thecrease_queries function at the same time)
    path_taken, private_data = util.chop_list_of_addrs(private_data)

    query_type = private_data[0:1]
    private_data = private_data[1:]

    for addr in path_taken:
        peer_increase_queries_answered(addr)

    print()
    print(f'{responder_addr=}')
    print(f'{query_type=}')
    print(f'{response=}')
    print(f'{path_taken=}')
    print(f'{private_data=}')

######
###### main
######

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
