#!/bin/sh
# One-step installer for tinyutils. It installs this checkout with the build tools already on this machine (no build isolation, so nothing is
# fetched for the build; the package has no dependencies) and nothing else; it makes no other network request.
set -e
pip install --no-input --no-build-isolation .
echo "tinyutils installed"
