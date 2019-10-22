#!/usr/bin/env bash

set -ex

circleci config process .circleci/config.yml > .circleci-config.yml

if [[ "$*" == "" ]]; then
    circleci local execute --config .circleci-config.yml --job test
    circleci local execute --config .circleci-config.yml --job test_python26
    circleci local execute --config .circleci-config.yml --job test_python33
    circleci local execute --config .circleci-config.yml --job xtest_python26
    circleci local execute --config .circleci-config.yml --job xtest_python27
    circleci local execute --config .circleci-config.yml --job xtest_python33
    circleci local execute --config .circleci-config.yml --job xtest_python34
    circleci local execute --config .circleci-config.yml --job xtest_python35
    circleci local execute --config .circleci-config.yml --job xtest_python36
    circleci local execute --config .circleci-config.yml --job xtest_python37
    circleci local execute --config .circleci-config.yml --job xtest_python38
    circleci local execute --config .circleci-config.yml --job xtest_pypy3
else
    circleci local execute --config .circleci-config.yml --job "$@"
fi
