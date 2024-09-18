#! /usr/bin/env bash

{
    set -euo pipefail

    PORT=6969

    trap 'kill -- -$$' EXIT
    # kill all children on exit

    ./check.sh

    ./alpha.py &
    ./beta.py $PORT &
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
