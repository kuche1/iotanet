#! /usr/bin/env bash

{
    set -euo pipefail

    MYPY='mypy --strict'

    $MYPY alpha.py
    $MYPY beta.py
    $MYPY beta_test.py
    $MYPY gamma.py
    $MYPY gamma_test.py
    $MYPY delta.py
}
