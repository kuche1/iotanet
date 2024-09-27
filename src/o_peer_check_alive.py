#! /usr/bin/env python3

# TODO
#
# perhaps there should be some sort of check so that it is waited for a bit until some of the peers are loaded
#
# also, this way of checking isn't too good (but not too terrible either)
# idelly we would randomly check for peers
#
# it kinds sucks that everyone knows when we wake up since we send a billion alive checks
#
# we could give the addresses of the messages being passed to us in order to find new peers

# TODO0 check for dead peers

import argparse
import time

from d_lib_peer import peer_get_known_addrs, peer_get_alive_addrs
from e_lib_query import QUERY_TYPE_CHECK_ALIVE, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
from m_query_send import send_query

def main() -> None:

    while True:

        for peer_addr in peer_get_known_addrs():

            extra_hops = 0
            # TODO
            # this CAN be changed to some other number, but someone along the way could drop the packet, and we would need to send multiple messages just to be sure
            # also do note that someone could just look at a singular node, then get info about the whole network if hops=0
            # same goes for the other loops here

            send_query(QUERY_TYPE_CHECK_ALIVE, b'', b'', peer_addr, extra_hops)
        
        time.sleep(10)

        for peer_addr in peer_get_alive_addrs():
            send_query(QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW, b'', b'', peer_addr, 0)

        time.sleep(60 * 5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: check peer alive')
    args = parser.parse_args()
    main()
