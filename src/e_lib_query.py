
import util
from util import Addr, Symetric_key

from a_send_1way import create_send_entry
from b_recv_1way import encrypt_symetric, FILE_PUBLIC_KEY
from d_lib_peer import peer_bytes_to_list_of_nodes, peer_create_or_update, peer_all_known_nodes_to_bytes, peer_mark_alive

QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY = b'0'

QUERY_TYPE_PING = b'1' # we could remove this one

QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW = b'2'

QUERY_TYPE_CHECK_ALIVE = b'3'
QUERY_TYPE_CHECK_ALIVE_YES = b'ye'

def answer_to_query(query_type:bytes, query:bytes, sym_key:Symetric_key, addr:Addr, query_id:bytes, return_path:bytes, resp_header:bytes) -> None:

    if query_type == QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY:

        assert len(query) == 0
        resp = util.file_read_bytes(FILE_PUBLIC_KEY)
    
    elif query_type == QUERY_TYPE_PING:

        resp = b'yes, I got your request: ' + query

    elif query_type == QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW:

        assert len(query) == 0
        resp = peer_all_known_nodes_to_bytes()
    
    elif query_type == QUERY_TYPE_CHECK_ALIVE:

        assert len(query) == 0
        resp = QUERY_TYPE_CHECK_ALIVE_YES

    else:

        assert False, f'unknown query type {query_type!r}'

    resp = resp_header + resp
    resp = encrypt_symetric(resp, sym_key)
    resp = return_path + resp

    create_send_entry(addr, resp)

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
    
    elif query_type == QUERY_TYPE_CHECK_ALIVE:

        assert response == QUERY_TYPE_CHECK_ALIVE_YES
        peer_mark_alive(responder_addr)
        print(f'{responder_addr} is alive')

    else:

        assert False, f'unknown query type {query_type!r}'

    # TODO wtf do we do with the private_data
