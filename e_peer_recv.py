#! /usr/bin/env python3

import os
import time
import argparse

import util
from util import echo as print

from a_send_1way import ITER_SLEEP_SEC
from c_circular import FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, FILENAME_RESPONDER_ADDR, FOLDER_RESPONSES
from d_peer_send import peer_increase_queries_answered

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_RECEIVED_MEASURED = f'{HERE}/_received_measured'

def handle_folder(path:str) -> None:

    # responder_addr = util.file_read_addr(f'{path}/{FILENAME_RESPONDER_ADDR}')
    private_data = util.file_read_bytes(f'{path}/{FILENAME_PRIVATE_DATA}')
    # response = util.file_read_bytes(f'{path}/{FILENAME_RESPONSE}')

    path_taken, private_data = util.chop_list_of_addrs(private_data)

    for addr in path_taken:
        peer_increase_queries_answered(addr)

    # print()
    # print(f'{responder_addr=}')
    # print(f'{private_data=}')
    # print(f'{response=}')
    print(f'{path_taken=}')

    root = util.gen_tmp_file_path()
    root_save = f'{FOLDER_RECEIVED_MEASURED}/{util.gen_rnd_filename()}'

    os.mkdir(root)

    util.copy(f'{path}/addr_{FILENAME_RESPONDER_ADDR}', f'{root}/{FILENAME_RESPONDER_ADDR}')
    util.file_write_bytes(f'{root}/{FILENAME_PRIVATE_DATA}', private_data)
    util.copy(f'{path}/{FILENAME_RESPONSE}', f'{root}/{FILENAME_RESPONSE}')

    util.move(root, root_save)

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, response_folders, _files in os.walk(FOLDER_RESPONSES):

            for response_folder in response_folders:

                path = f'{FOLDER_RESPONSES}/{response_folder}'

                util.try_finally(
                    lambda: handle_folder(path),
                    lambda: util.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: peer recv')
    args = parser.parse_args()
    main()
