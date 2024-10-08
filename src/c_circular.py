#! /usr/bin/env python3

import time
import os
import argparse
import errno

import util
from util import echo as print
from util import Symetric_key, SYMETRIC_KEY_SIZE_BYTES, SYMETRIC_KEY_IV_SIZE_BYTES, Node

from a_send_1way import ITER_SLEEP_SEC, create_send_entry
from b_recv_1way import send_1way, generate_send_1way_header, encrypt_symetric, FOLDER_RECEIVED_UNPROCESSED, generate_symetric_key, decrypt_symetric

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_REQUESTS = f'{HERE}/_requests'
FOLDER_REQUESTS_TMP = f'{FOLDER_REQUESTS}_tmp'

FOLDER_RESPONSES = f'{HERE}/_responses'
FOLDER_RESPONSES_TMP = f'{FOLDER_RESPONSES}_tmp'

FILE_IDENTIFICATOR_KEY = f'{HERE}/_identificator_key'

FILENAME_RESPONDER_ADDR = 'responder_addr'
FILENAME_PRIVATE_DATA = 'private_data'
FILENAME_RESPONSE = 'response'
FILENAME_ADDR = 'addr'

MESSAGE_TYPE_REQUEST = b'0'
MESSAGE_TYPE_RESPONSE = b'1'

SEP = b':'

def chop_until_next_sep(payload:bytes) -> tuple[str, bytes, bytes]:

    idx = payload.find(SEP)

    if idx <= 0:
        return 'no separator found', b'', payload
    
    data = payload[:idx]
    payload = payload[idx + len(SEP):]

    return '', data, payload

def send_circular(query:bytes, private_data:bytes, path_to_dest:list[Node], path_way_back:list[Node]) -> None:

    dest_addr, _dest_pub = path_to_dest[-1]
    private_data = util.addr_to_bytes(dest_addr) + private_data

    addr_back, header_back, response_sym_key = generate_send_1way_header(path_way_back)

    private_data = encrypt_symetric(
        private_data,
        util.file_read_symetric_key(FILE_IDENTIFICATOR_KEY)
    )

    payload = \
        MESSAGE_TYPE_REQUEST + \
        str(len(query)).encode() + SEP + \
        query + \
        util.symetric_key_to_bytes(response_sym_key) + \
        util.addr_to_bytes(addr_back) + \
        str(len(private_data)).encode() + SEP + \
        private_data + \
        header_back

    send_1way(payload, path_to_dest)

def handle_file(path:str, message_file:str) -> None:

    data = util.file_read_bytes(path)

    assert len(data) > 0

    type_ = data[0:1]
    payload = data[1:]

    if type_ == MESSAGE_TYPE_REQUEST:

        # print()
        # print(f'got request: {payload!r}')
        # print()

        err, query_len_bytes, payload = chop_until_next_sep(payload)
        assert not err
        
        query_len = int(query_len_bytes)

        assert query_len >= 0

        assert query_len <= len(payload)

        query = payload[:query_len]
        payload = payload[query_len:]

        sym_key, payload = util.chop_symetric_key(payload)

        addr, payload = util.chop_addr(payload)

        err, query_id_len_bytes, payload = chop_until_next_sep(payload)
        assert not err
        
        query_id_len = int(query_id_len_bytes)

        assert query_id_len >= 0

        query_id = payload[:query_id_len]
        payload = payload[query_id_len:]

        assert len(query_id) == query_id_len
        
        return_path = payload

        # print()
        # print(f'{query_len=}')
        # print(f'{query=}')
        # print(f'{sym_key=}')
        # print(f'{addr=}')
        # print(f'{query_id_len=}')
        # print(f'{query_id=}')
        # print(f'{return_path=}')
        # print()

        root_tmp = f'{FOLDER_REQUESTS_TMP}/{message_file}'
        root_saved = f'{FOLDER_REQUESTS}/{message_file}'

        os.mkdir(root_tmp)

        with open(f'{root_tmp}/query', 'wb') as f:
            f.write(query)

        util.file_write_symetric_key(f'{root_tmp}/sym_key', sym_key)

        util.file_write_addr(f'{root_tmp}/{FILENAME_ADDR}', addr)

        with open(f'{root_tmp}/id', 'wb') as f:
            f.write(query_id)

        with open(f'{root_tmp}/return_path', 'wb') as f:
            f.write(return_path)
        
        util.move(root_tmp, root_saved)

    elif type_ == MESSAGE_TYPE_RESPONSE:

        # print()
        # print(f'got response: {payload!r}')
        # print()

        err, query_id_len_bytes, payload = chop_until_next_sep(payload)
        assert not err

        query_id_len = int(query_id_len_bytes)

        assert query_id_len >= 0

        private_data = payload[:query_id_len]
        payload = payload[query_id_len:]

        private_data = decrypt_symetric(
            private_data,
            util.file_read_symetric_key(FILE_IDENTIFICATOR_KEY)
        )

        responder_addr, private_data = util.chop_addr(private_data)

        query_response = payload
        
        # print(f'{private_data=}')
        # print(f'{query_response=}')

        root_tmp = f'{FOLDER_RESPONSES_TMP}/{message_file}'
        root_saved = f'{FOLDER_RESPONSES}/{message_file}'

        os.mkdir(root_tmp)

        util.file_write_addr(f'{root_tmp}/{FILENAME_RESPONDER_ADDR}', responder_addr)

        util.file_write_bytes(f'{root_tmp}/{FILENAME_PRIVATE_DATA}', private_data) 

        util.file_write_bytes(f'{root_tmp}/{FILENAME_RESPONSE}', query_response)
        
        util.move(root_tmp, root_saved)

    else:

        print()
        print(f'invalid type {type_!r}')
        print(f'payload: {payload!r}')
        print()

def process_messages() -> None:

    os.makedirs(FOLDER_REQUESTS, exist_ok=True)
    os.makedirs(FOLDER_REQUESTS_TMP, exist_ok=True)

    os.makedirs(FOLDER_RESPONSES, exist_ok=True)
    os.makedirs(FOLDER_RESPONSES_TMP, exist_ok=True)

    while True:

        time.sleep(ITER_SLEEP_SEC)

        message_files:list[str] = []
        for _path, _folders, message_files in os.walk(FOLDER_RECEIVED_UNPROCESSED):
            break
        
        for message_file in message_files:

            path = f'{FOLDER_RECEIVED_UNPROCESSED}/{message_file}'

            def remove_the_file() -> None:
                try:
                    os.remove(path)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise

            util.try_finally(
                lambda: handle_file(path, message_file),
                remove_the_file,
            )

def main() -> None:

    util.file_write_symetric_key(FILE_IDENTIFICATOR_KEY, generate_symetric_key())

    print('generated new identity key')

    process_messages()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: circular messages')
    args = parser.parse_args()

    main()
