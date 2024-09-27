#! /usr/bin/env bash

{
    set -euo pipefail

    HERE=$(dirname $(realpath $BASH_SOURCE))

    MYPY='mypy --strict --no-incremental'
    # without `--no-incremental` doesnt always work

    cd "$HERE/src"

    if [ $# -ne 1 ]; then
        echo 'you need to give exactly 1 argument - port'
        exit 1
    fi

    port="$1"

    trap 'kill -- -$$' EXIT
    # kill all children on exit

    $MYPY \
        ./util.py \
        ./util_test.py \
        ./a_send_1way.py \
        ./b_recv_1way.py \
        ./c_circular.py \
        ./e_peer_check_alive.py \
        ./h_peer_send.py \
        ./i_peer_recv.py \
        ./j_lib_query.py \
        ./k_query_recv_process.py \
        ./m_query_send.py \
        ./m_query_send_test.py

    ./util.py
    ./a_send_1way.py &
    ./b_recv_1way.py $port &
    sleep 0.1
    ./c_circular.py &
    #./e_peer_check_alive.py &
    ./h_peer_send.py &
    ./i_peer_recv.py &
    ./k_query_recv_process.py &
    ./m_query_send.py &

    echo '~~{{(( all started ))}}~~'

    wait -n
    # wait for anyone to exit

    # if anyone has exited, this must be an error
    exit 1
}
