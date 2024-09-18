#! /usr/bin/env python3

# WIP
# idk if this is even relevant anymore

import os

from beta import FOLDER_RECEIVED_UNPROCESSED

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_RECEIVED = f'{HERE}/_received'
FOLDER_RECEIVED_TMP = f'{FOLDER_RECEIVED}_tmp'

CMD_PUSH = b'0'

CMD_GET_PUB_KEY = b'1'

def main():

    os.makedirs(FOLDER_RECEIVED, exist_ok=True)

    while True:

        message_files = []
        for _path, _folders, message_files in os.walk(FOLDER_RECEIVED_UNPROCESSED):
            break
        
        for file in message_files:

            path_source = f'{FOLDER_RECEIVED_UNPROCESSED}/{file}'
            path_tmp = f'{FOLDER_RECEIVED_TMP}/file'
            path_dest = f'{FOLDER_RECEIVED}/{file}'

            with open(path_source, 'rb') as f:
                message = f.read()
            
            if len(message) <= 0:
                print('bad message')
                os.remove(path_source)
                continue
            
            cmd = message[0:1]
            args = message[1:]

            if cmd == CMD_PUSH:

                with open(path_tmp, 'wb') as f:
                    f.write(args)
                
                os.remove(cmd)

                shutil.move(path_tmp, path_dest)

            else:

                print(f'unknown command: {cmd!r}')

main()