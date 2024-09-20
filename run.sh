#! /usr/bin/env bash

{
    set -euo pipefail

    MYPY='mypy --strict --no-incremental'
    # without `--no-incremental` doesnt always work

    if [ $# -ne 1 ]; then
        echo 'you need to give exactly 1 argument - port'
        exit 1
    fi

    port="$1"

    trap 'kill -- -$$' EXIT
    # kill all children on exit

    $MYPY \
        util.py \
        util_test.py \
        a_send_1way.py \
        b_recv_1way.py \
        c_circular.py \
        c_circular_test.py \
        d_peer.py \
        e_recv_query.py \
        e_recv_query_test.py \
        f_send_process_query.py \
        f_send_process_query_test.py

    ./a_send_1way.py &
    ./b_recv_1way.py $port &
    sleep 0.1
    ./c_circular.py &
    ./d_peer.py &
    ./e_recv_query.py &
    ./f_send_process_query.py &

    echo '~~{{(( all started ))}}~~'

    wait -n
    # wait for anyone to exit

    # if anyone has exited, this must be an error
    exit 1
}
