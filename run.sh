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

    $MYPY util.py

    $MYPY alpha.py
    ./alpha.py &

    $MYPY beta.py
    $MYPY beta_test.py
    ./beta.py $port &

    $MYPY gamma.py
    $MYPY gamma_test.py
    ./gamma.py &

    $MYPY delta.py
    $MYPY delta_test.py
    ./delta.py &

    $MYPY epsilon.py
    ./epsilon.py &

    # zeta
    # eta
    # theta
    # iota
    # kappa
    # lambda
    # mu
    # nu
    # xi
    # omicron
    # pi
    # rho
    # sigma
    # tau
    # upsilon
    # phi
    # chi
    # psi
    # omega

    echo 'all started'

    wait -n
    # wait for anyone to exit

    # if anyone has exited, this must be an error
    exit 1
}
