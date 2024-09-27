#! /usr/bin/env python3

# TODO
#
# perhaps there should be some sort of check so that it is waited for a bit until some of the peers are loaded
#
# also, this way of checking isn't too good (but not too terrible either)
# idelly we would randomly check for peers

# TODO0 check for dead peers

import argparse
import time

from d_lib_peer import peer_get_known_addrs
from e_lib_query import QUERY_TYPE_CHECK_ALIVE
from m_query_send import send_query

SLEEP_ITER_SEC = 60 * 5

def main() -> None:

    while True:

        for peer_addr in peer_get_known_addrs():

            extra_hops = 0
            # TODO
            # this CAN be changed to some other number, but someone along the way could drop the packet, and we would need to send multiple messages just to be sure
            # also do note that someone could just look at a singular node, then get info about the whole network if hops=0

            send_query(QUERY_TYPE_CHECK_ALIVE, b'', b'', peer_addr, extra_hops)
        
        time.sleep(SLEEP_ITER_SEC)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: check peer alive')
    args = parser.parse_args()
    main()
