#!/bin/sh
# One-step installer for tinyutils. It installs this checkout (which has no dependencies) and nothing else; it makes no other network request.
set -e
pip install --no-input .
echo "tinyutils installed"
