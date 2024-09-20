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
        beta.py \
        beta_test.py \
        gamma.py \
        gamma_test.py \
        delta.py \
        delta_test.py \
        epsilon.py \
        epsilon_test.py

    ./a_send_1way.py &
    ./beta.py $port &
    sleep 0.1
    ./gamma.py &
    ./delta.py &
    ./epsilon.py &

    echo '~~{{(( all started ))}}~~'

    wait -n
    # wait for anyone to exit

    # if anyone has exited, this must be an error
    exit 1
}
