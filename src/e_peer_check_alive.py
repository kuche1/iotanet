#! /usr/bin/env python3

# TODO implement this

import argparse

def main() -> None:
    pass

    # for peer_addr in peer_addrs_TODO:

    #     extra_hops = 0
    #     # TODO
    #     # this CAN be changed to some other number, but someone along the way could drop the packet, and we would need to send multiple messages just to be sure
    #     # also do note that someone could just look at a singular node, then get info about the whole network if hops=0

    #     send_query(QUERY_TYPE_CHECK_ALIVE, b'', peer_addr, extra_hops)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: check peer alive')
    args = parser.parse_args()
    main()
