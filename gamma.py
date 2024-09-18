#! /usr/bin/env python3

import time
import os
import argparse
import shutil
import errno

import util
from util import Symetric_key, SYMETRIC_KEY_SIZE_BYTES, SYMETRIC_KEY_IV_SIZE_BYTES

from alpha import ITER_SLEEP_SEC, create_send_entry
from beta import Node, send_1way, generate_send_1way_header, encrypt_symetric, FOLDER_RECEIVED_UNPROCESSED, generate_symetric_key, decrypt_symetric

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_REQUESTS = f'{HERE}/_requests'
FOLDER_REQUESTS_TMP = f'{FOLDER_REQUESTS}_tmp'

FOLDER_RESPONSES = f'{HERE}/_responses'
FOLDER_RESPONSES_TMP = f'{FOLDER_RESPONSES}_tmp'

FILE_IDENTIFICATOR_KEY = f'{HERE}/_identificator_key'

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

def send_circular(query:bytes, query_id:bytes, path_to_dest:list[Node], path_way_back:list[Node]) -> None:

    (ip_back, port_back), header_back, response_sym_key, response_sym_iv = generate_send_1way_header(path_way_back)

    identificator_sym_key, identificator_sym_iv = util.file_read_symetric_key(FILE_IDENTIFICATOR_KEY)

    query_identificator = encrypt_symetric(query_id, identificator_sym_key, identificator_sym_iv)

    payload = \
        MESSAGE_TYPE_REQUEST + \
        str(len(query)).encode() + SEP + \
        query + \
        response_sym_key + \
        response_sym_iv + \
        ip_back.encode() + SEP + \
        str(port_back).encode() + SEP + \
        str(len(query_identificator)).encode() + SEP + \
        query_identificator + \
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

        sym_key = payload[:SYMETRIC_KEY_SIZE_BYTES]
        payload = payload[SYMETRIC_KEY_SIZE_BYTES:]
        assert len(sym_key) == SYMETRIC_KEY_SIZE_BYTES

        sym_iv = payload[:SYMETRIC_KEY_IV_SIZE_BYTES]
        payload = payload[SYMETRIC_KEY_IV_SIZE_BYTES:]
        assert len(sym_iv) == SYMETRIC_KEY_IV_SIZE_BYTES

        err, ip_bytes, payload = chop_until_next_sep(payload)
        assert not err

        ip = ip_bytes.decode()

        err, port_bytes, payload = chop_until_next_sep(payload)
        assert not err

        port = int(port_bytes)
        assert port > 0

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
        # print(f'{sym_iv=}')
        # print(f'{ip=}')
        # print(f'{port=}')
        # print(f'{query_id_len=}')
        # print(f'{query_id=}')
        # print(f'{return_path=}')
        # print()

        root_tmp = f'{FOLDER_REQUESTS_TMP}/{message_file}'
        root_saved = f'{FOLDER_REQUESTS}/{message_file}'

        os.mkdir(root_tmp)

        with open(f'{root_tmp}/query', 'wb') as f:
            f.write(query)

        with open(f'{root_tmp}/sym_key', 'wb') as f:
            f.write(sym_key)

        with open(f'{root_tmp}/sym_iv', 'wb') as f:
            f.write(sym_iv)

        with open(f'{root_tmp}/ip', 'w') as f:
            f.write(ip)

        with open(f'{root_tmp}/port', 'w') as f:
            f.write(str(port))

        with open(f'{root_tmp}/id', 'wb') as f:
            f.write(query_id)

        with open(f'{root_tmp}/return_path', 'wb') as f:
            f.write(return_path)
        
        shutil.move(root_tmp, root_saved)

    elif type_ == MESSAGE_TYPE_RESPONSE:

        # print()
        # print(f'got response: {payload!r}')
        # print()

        err, query_id_len_bytes, payload = chop_until_next_sep(payload)
        assert not err

        query_id_len = int(query_id_len_bytes)

        assert query_id_len >= 0

        query_id = payload[:query_id_len]
        payload = payload[query_id_len:]

        id_key, id_iv = util.file_read_symetric_key(FILE_IDENTIFICATOR_KEY)
        query_id = decrypt_symetric(query_id, id_key, id_iv)

        query_response = payload
        
        # print(f'{query_id=}')
        # print(f'{query_response=}')

        root_tmp = f'{FOLDER_RESPONSES_TMP}/{message_file}'
        root_saved = f'{FOLDER_RESPONSES}/{message_file}'

        os.mkdir(root_tmp)

        with open(f'{root_tmp}/id', 'wb') as f:
            f.write(query_id)

        with open(f'{root_tmp}/response', 'wb') as f:
            f.write(query_response)
        
        shutil.move(root_tmp, root_saved)

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
