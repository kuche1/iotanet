#! /usr/bin/env python3

import argparse
import time
import os
import shutil
import random

import util
from util import Node, Addr, Public_key

from alpha import ITER_SLEEP_SEC
from beta import FILE_PUBLIC_KEY, FILE_PORT
from gamma import FOLDER_RESPONSES, FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, send_circular, FILENAME_SENDER_ADDR

HERE = os.path.dirname(os.path.realpath(__file__))

######
###### send fnc
######

def send_query(query_type:bytes, query_args:bytes, private_data:bytes, dest:Node, me:Node, extra_hops:int) -> None:

    assert len(query_type) == 1

    query = query_type + query_args

    # TODO
    # I'm no sure if this logic should be here, or in `send_circular`, or even somewhere on a higher level
    # (actually, the more I think about it, the better of an idea seems that this peer evaluation thing should be in `send_circular` and the path selection too)

    path:list[Node] = []
    for _ in range(extra_hops):
        path.append(peer_get_random_node())

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

    # TODO
    # for addr, _pub in path_without_me:
    #     util.peer_increase_queries_sent(addr)

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

    # TODO
    # for addr in path_taken:
    #     util.peer_increase_queries_answered(addr)

    print('epsilon:')
    print(f'epsilon: {sender_addr=}')
    print(f'epsilon: {query_type=}')
    print(f'epsilon: {response=}')
    print(f'epsilon: {path_taken=}')
    print(f'epsilon: {private_data=}')

######
###### peer-related
######

FOLDER_PEERS = f'{HERE}/_peers'

PEER_FILENAME_PUBLIC_KEY = 'public_key'

def peer_update(addr:Addr, pub:Public_key) -> None:
    
    folder_name = util.addr_to_str(addr)

    peer_folder = f'{FOLDER_PEERS}/{folder_name}'

    os.makedirs(peer_folder, exist_ok=True)

    util.file_write_public_key(f'{peer_folder}/{PEER_FILENAME_PUBLIC_KEY}', pub)

def peer_get_folders() -> list[str]:
    files:list[str] = []
    for path, folders, _files in os.walk(FOLDER_PEERS):
        files = [f'{path}/{folder}' for folder in folders]
        break
    return files

def peer_folder_read_node(path:str) -> Node:
    peer_addr_str = os.path.basename(path)

    peer_addr, nothing = util.chop_addr_from_str(peer_addr_str)
    assert len(nothing) == 0

    peer_pub = util.file_read_public_key(f'{path}/{PEER_FILENAME_PUBLIC_KEY}')

    return (peer_addr, peer_pub)

def peer_get_random_node() -> Node:
    folders = peer_get_folders()
    folder = random.choice(folders)
    peer = peer_folder_read_node(folder)
    return peer

######
###### main
######

def main() -> None:

    os.makedirs(FOLDER_PEERS, exist_ok=True)

    peer_update(
        ('127.0.0.1', util.file_read_port(FILE_PORT)),
        util.file_read_public_key(FILE_PUBLIC_KEY),
    )
    # TODO stupid

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
