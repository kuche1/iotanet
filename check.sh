#! /usr/bin/env bash

{
    set -euo pipefail

    MYPY='mypy --strict'

    $MYPY epsilon.py
    $MYPY zeta.py
}
