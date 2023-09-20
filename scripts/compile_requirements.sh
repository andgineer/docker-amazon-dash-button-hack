#!/usr/bin/env bash
#
# Pin current dependencies versions.
#

rm -f requirements.txt
rm -f requirements.dev.txt

# we should process requirements.in first because it's included in requirements.dev.in
pip-compile requirements.in
pip-compile requirements.dev.in
