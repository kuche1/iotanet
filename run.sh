#! /usr/bin/env bash

{
    set -euo pipefail

    SLEEP='0.2'

    if [ $# -ne 1 ]; then
        echo 'you need to give exactly 1 argument - port'
        exit 1
    fi

    port="$1"

    trap 'kill -- -$$' EXIT
    # kill all children on exit

    ./check.sh

    ./alpha.py &
    sleep $SLEEP
    ./beta.py $port &
    sleep $SLEEP
    ./gamma.py &
    sleep $SLEEP
    ./delta.py &
    sleep $SLEEP
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
