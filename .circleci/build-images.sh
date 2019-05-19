#!/usr/bin/env bash
DATE=$(date -I)
docker build -t danielflook/python-minifier-build:fedora30-$DATE -f Dockerfile-fedora30 .
docker build -t danielflook/python-minifier-build:fedora28-$DATE -f Dockerfile-fedora28 .
