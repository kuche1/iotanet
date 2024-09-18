#! /usr/bin/env bash

{
    set -euo pipefail

    if [ $# -ne 1 ]; then
        echo 'you need to give exactly 1 argument - port'
        exit 1
    fi

    port="$1"

    trap 'kill -- -$$' EXIT
    # kill all children on exit

    ./check.sh

    ./alpha.py &
    ./beta.py $port &
    ./gamma.py &
    ./delta.py &
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

    wait -n
    # wait for anyone to exit

    # if anyone has exited, this must be an error
    exit 1
}
