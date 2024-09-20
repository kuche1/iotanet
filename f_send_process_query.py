#! /usr/bin/env python3

import argparse
import time
import os
import shutil
import random

import util
from util import echo as print
from util import Node

from a_send_1way import ITER_SLEEP_SEC
from c_circular import FOLDER_RESPONSES, FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, send_circular, FILENAME_SENDER_ADDR
from d_peer import peer_get_random_nodes_based_on_reliability, peer_increase_queries_sent, peer_increase_queries_answered

######
###### send fnc
######

def send_query(query_type:bytes, query_args:bytes, private_data:bytes, dest:Node, me:Node, extra_hops:int) -> None:

    assert len(query_type) == 1

    query = query_type + query_args

    path:list[Node] = peer_get_random_nodes_based_on_reliability(extra_hops)

    split_idx = random.randint(0, len(path)-1)

    path_to_dest = path[:split_idx] + [dest]
    path_way_back = path[split_idx:] + [me]

    path_without_me = path_to_dest + path_way_back[:-1]
    private_data = query_type + util.list_of_nodes_to_bytes_of_node_addrs(path_without_me) + private_data

    send_circular(
        query,
        private_data,
        path_to_dest,
        path_way_back,
    )

    for addr, _pub in path_without_me:
        peer_increase_queries_sent(addr)

######
###### process query answer
######

def handle_folder(path:str) -> None:

    sender_addr = util.file_read_addr(f'{path}/{FILENAME_SENDER_ADDR}')
    private_data = util.file_read_bytes(f'{path}/{FILENAME_PRIVATE_DATA}')
    response = util.file_read_bytes(f'{path}/{FILENAME_RESPONSE}')

    assert len(private_data) > 0

    query_type = private_data[0:1]
    private_data = private_data[1:]

    path_taken, private_data = util.chop_list_of_addrs(private_data)

    for addr in path_taken:
        peer_increase_queries_answered(addr)

    print()
    print(f'{sender_addr=}')
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
