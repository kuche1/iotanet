#! /usr/bin/env bash

{
    set -euo pipefail
    mypy --strict zeta.py
    python3 zeta.py $@
}
