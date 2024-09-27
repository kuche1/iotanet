
from util import Addr

from g_peer_send import peer_bytes_to_list_of_nodes, peer_create_or_update

QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY = b'0'
QUERY_TYPE_PING = b'1' # we could remove this one
QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW = b'2'

def process_query_answer(query_type:bytes, response:bytes, responder_addr:Addr, private_data:bytes) -> None:

    # print()
    # print(f'{responder_addr=}')
    # print(f'{query_type=}')
    # print(f'{response=}')
    # print(f'{private_data=}')
    # print()

    if query_type == QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY:

        print(f'I got {responder_addr}\'s public key {response!r}')

    elif query_type == QUERY_TYPE_PING:

        print(f'{responder_addr} answered to my ping with {response!r}')
    
    elif query_type == QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW:

        nodes = peer_bytes_to_list_of_nodes(response)

        print(f'{responder_addr} knows the following pers: {nodes}')

        print('updaing peer list...')

        for node in nodes:
            addr, pub = node
            peer_create_or_update(addr, pub)
            # TODO we should be checking if the public keys match, and try and deduce who is lying

        print('peer list updated')
    
    else:

        assert False, f'unknown query type {query_type!r}'

    # TODO wtf do we do with the private_data
