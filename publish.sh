#!/usr/bin/env bash
set -e

python3 setup.py test -q

rm dist/* || echo '/dist is empty'
python3 setup.py sdist bdist_wheel

read -r -p "Tests and build complete. Press [Enter] to publish..."

python3 -m twine upload dist/*
