#!/bin/sh
# One-step installer for tinyutils. It installs the pinned requirements and nothing else; it makes no other network request.
set -e
pip install --no-input --require-hashes -r requirements.txt
echo "tinyutils installed"
