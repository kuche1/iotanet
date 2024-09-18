#! /usr/bin/env python3

# TODO this can crash

import time
import os
import argparse

from alpha import ITER_SLEEP_SEC, create_send_entry
from beta import Node, send_1way, Symetric_key, generate_send_1way_header, encrypt_symetric, FOLDER_RECEIVED_UNPROCESSED, generate_symetric_key, SYMETRIC_KEY_SIZE_BYTES, SYMETRIC_KEY_IV_SIZE_BYTES

TYPE_REQUEST = b'0'
TYPE_RESPONSE = b'1'

SEP = b':'

def chop_until_next_sep(payload:bytes) -> tuple[str, bytes, bytes]:

    idx = payload.find(SEP)

    if idx <= 0:
        return 'no separator found', b'', payload
    
    data = payload[:idx]
    payload = payload[idx + len(SEP):]

    return '', data, payload

def send_circular(query:bytes, query_id:bytes, path_to_dest:list[Node], path_way_back:list[Node]) -> tuple[Symetric_key, int, Symetric_key]:

    (ip_back, port_back), header_back, response_sym_key, response_sym_iv = generate_send_1way_header(path_way_back)

    identificator_sym_key, identificator_sym_iv = generate_symetric_key()

    query_identificator = encrypt_symetric(query_id, identificator_sym_key, identificator_sym_iv)

    payload = \
        TYPE_REQUEST + \
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

    return (identificator_sym_key, identificator_sym_iv), len(query_identificator), (response_sym_key, response_sym_iv)

def process_messages() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        message_files:list[str] = []
        for _path, _folders, message_files in os.walk(FOLDER_RECEIVED_UNPROCESSED):
            break
        
        for file in message_files:

            path = f'{FOLDER_RECEIVED_UNPROCESSED}/{file}'

            with open(path, 'rb') as f:
                data = f.read()

            if len(data) <= 0:
                print('empty message')
                os.remove(path)
                continue

            type_ = data[0:1]
            payload = data[1:]

            if type_ == TYPE_REQUEST:

                print()
                print(f'got request: {payload!r}')
                print()

                err, query_len_bytes, payload = chop_until_next_sep(payload)

                if err:
                    print(f'cant get query len: {err}')
                    os.remove(path)
                    continue
                
                try:
                    query_len = int(query_len_bytes)
                except ValueError:
                    print('non-number query length')
                    os.remove(path)
                    continue

                if query_len < 0:
                    print('negative query length')
                    os.remove(path)
                    continue
                
                if query_len > len(payload):
                    print('query length more than payload length')
                    os.remove(path)
                    continue

                query = payload[:query_len]
                payload = payload[query_len:]

                sym_key = payload[:SYMETRIC_KEY_SIZE_BYTES]
                payload = payload[SYMETRIC_KEY_SIZE_BYTES:]
                if len(sym_key) != SYMETRIC_KEY_SIZE_BYTES:
                    print('partal sym_key')
                    os.remove(path)
                    continue

                sym_iv = payload[:SYMETRIC_KEY_IV_SIZE_BYTES]
                payload = payload[SYMETRIC_KEY_IV_SIZE_BYTES:]
                if len(sym_iv) != SYMETRIC_KEY_IV_SIZE_BYTES:
                    print('partal sym_iv')
                    os.remove(path)
                    continue

                err, ip_bytes, payload = chop_until_next_sep(payload)

                ip = ip_bytes.decode()

                err, port_bytes, payload = chop_until_next_sep(payload)

                try:
                    port = int(port_bytes)
                except ValueError:
                    print('invalid port')
                    os.remove(path)
                    continue

                err, query_id_len_bytes, payload = chop_until_next_sep(payload)
                if err:
                    print(f'could not determine query id length: {err}')
                    os.remove(path)
                    continue
                
                try:
                    query_id_len = int(query_id_len_bytes)
                except ValueError:
                    print('query id len is not a number')
                    os.remove(path)
                    continue

                if query_id_len < 0:
                    print('query id len < 0')
                    os.remove(path)
                    continue

                query_id = payload[:query_id_len]
                payload = payload[query_id_len:]

                if len(query_id) != query_id_len:
                    print('invalid query id len')
                    os.remove(path)
                    continue

                print()
                print(f'{query_len=}')
                print(f'{query=}')
                print(f'{sym_key=}')
                print(f'{sym_iv=}')
                print(f'{ip=}')
                print(f'{port=}')
                print(f'{query_id_len=}')
                print(f'{query_id=}')
                print(f'{payload=}')
                print()

                resp = b'yes, I got your request: ' + query

                print(f'{resp=}')

                resp = TYPE_RESPONSE + query_id_len_bytes + SEP + query_id + resp

                print(f'{resp=}')

                resp = encrypt_symetric(resp, sym_key, sym_iv)

                print(f'{resp=}')

                payload = payload + resp

                create_send_entry(ip, port, payload)

            elif type_ == TYPE_RESPONSE:

                print()
                print(f'got response: {payload!r}')
                print()

                err, query_id_len_bytes, payload = chop_until_next_sep(payload)
                if err:
                    print(f'could not determine query id length: {err}')
                    os.remove(path)
                    continue

                try:
                    query_id_len = int(query_id_len_bytes)
                except ValueError:
                    print('query id len not an int')
                    os.remove(path)
                    continue

                if query_id_len < 0:
                    print(f'query id len < 0')
                    os.remove(path)
                    continue

                query_id = payload[:query_id_len] # TODO this is the encrypted version
                payload = payload[query_id_len:]

                query_response = payload
                
                print(f'{query_id_len=}')
                print(f'{query_id=}')
                print(f'{query_response=}')

            else:

                print()
                print(f'invalid type {type_!r}')
                print(f'payload: {payload!r}')
                print()

            os.remove(path)

def main() -> None:
    process_messages()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: circular messages')
    args = parser.parse_args()

    main()
