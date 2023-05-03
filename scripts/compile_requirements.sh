#!/usr/bin/env bash
#
# Pin current dependencies versions.
#

rm -f requirements.txt
rm -f requirements.test.txt

pip-compile requirements.in
pip-compile requirements.test.in
