#! /usr/bin/env bash

{
    set -euo pipefail
    mypy --strict epsilon.py
    python3 epsilon.py $@
}
