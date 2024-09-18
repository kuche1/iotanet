#! /usr/bin/env bash

{
    set -euo pipefail

    MYPY='mypy --strict'

    $MYPY alpha.py
    $MYPY beta.py
    $MYPY beta_test.py
}
