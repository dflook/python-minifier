#!/usr/bin/env bash

set -eo pipefail

DATE=$(date -I)

docker pull fedora:28
docker build --tag danielflook/python-minifier-build:python3.3-$DATE -f Dockerfile-fedora28 --target python3.3 .

docker pull fedora:30
docker build --tag danielflook/python-minifier-build:python2.7-$DATE -f Dockerfile-fedora30 --target python2.7 .
docker build --tag danielflook/python-minifier-build:python3.4-$DATE -f Dockerfile-fedora30 --target python3.4 .
docker build --tag danielflook/python-minifier-build:python3.5-$DATE -f Dockerfile-fedora30 --target python3.5 .
docker build --tag danielflook/python-minifier-build:python3.6-$DATE -f Dockerfile-fedora30 --target python3.6 .
docker build --tag danielflook/python-minifier-build:python3.7-$DATE -f Dockerfile-fedora30 --target python3.7 .
docker build --tag danielflook/python-minifier-build:python3.8-$DATE -f Dockerfile-fedora30 --target python3.8 .
docker build --tag danielflook/python-minifier-build:pypy-$DATE -f Dockerfile-fedora30 --target pypy .
docker build --tag danielflook/python-minifier-build:pypy3-$DATE -f Dockerfile-fedora30 --target pypy3 .

docker pull fedora:32
docker build --tag danielflook/python-minifier-build:python3.9-$DATE -f Dockerfile-fedora32 --target python3.9 .

docker pull fedora:34
docker build --tag danielflook/python-minifier-build:python3.10-$DATE -f Dockerfile-fedora34 --target python3.10 .

docker pull fedora:36
docker build --tag danielflook/python-minifier-build:python3.11-$DATE -f Dockerfile-fedora36 --target python3.11 .

docker pull fedora:38
docker build --tag danielflook/python-minifier-build:python3.12-$DATE -f Dockerfile-fedora38 --target python3.12 .

docker pull fedora:40
docker build --tag danielflook/python-minifier-build:python3.13-$DATE -f Dockerfile-fedora40 --target python3.13 .

docker pull fedora:42
docker build --tag danielflook/python-minifier-build:python3.14-$DATE -f Dockerfile-fedora42 --target python3.14 .

docker build --tag danielflook/python-minifier-build:fuzz-$DATE -f Dockerfile-fuzz --target fuzz .

docker push danielflook/python-minifier-build:python3.3-$DATE
docker push danielflook/python-minifier-build:python2.7-$DATE
docker push danielflook/python-minifier-build:python3.4-$DATE
docker push danielflook/python-minifier-build:python3.5-$DATE
docker push danielflook/python-minifier-build:python3.6-$DATE
docker push danielflook/python-minifier-build:python3.7-$DATE
docker push danielflook/python-minifier-build:python3.8-$DATE
docker push danielflook/python-minifier-build:python3.9-$DATE
docker push danielflook/python-minifier-build:python3.10-$DATE
docker push danielflook/python-minifier-build:python3.11-$DATE
docker push danielflook/python-minifier-build:python3.12-$DATE
docker push danielflook/python-minifier-build:python3.13-$DATE
docker push danielflook/python-minifier-build:python3.14-$DATE
docker push danielflook/python-minifier-build:pypy-$DATE
docker push danielflook/python-minifier-build:pypy3-$DATE
docker push danielflook/python-minifier-build:fuzz-$DATE
