#!/usr/bin/env bash

set -ex

circleci config process .circleci/config.yml > .circleci-config.yml

if [[ "$*" == "" ]]; then
    circleci local execute --config .circleci-config.yml --job test
    circleci local execute --config .circleci-config.yml --job test_python33
    circleci local execute --config .circleci-config.yml --job test_python39
    circleci local execute --config .circleci-config.yml --job test_python310
else
    circleci local execute --config .circleci-config.yml --job "$@"
fi
