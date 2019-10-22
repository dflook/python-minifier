#!/usr/bin/env bash

DATE=$(date -I)

docker build -t danielflook/python-minifier-build:fedora30-$DATE -f Dockerfile-fedora30 . --no-cache --pull
docker build -t danielflook/python-minifier-build:fedora28-$DATE -f Dockerfile-fedora28 . --no-cache --pull

docker push danielflook/python-minifier-build:fedora30-$DATE
docker push danielflook/python-minifier-build:fedora28-$DATE
