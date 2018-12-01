# This file should be pushed to danielflook/python-minifier-build
FROM fedora:28

# CircleCI required tools
RUN dnf install -y \
      git \
      openssh \
      tar \
      gzip \
      gpg \
      ca-certificates

# Python versions
RUN dnf install -y \
      python26 \
      python27 \
      python33 \
      python34 \
      python35 \
      python36 \
      python37 \
      pypy \
      pypy3 \
      python2-test \
      python3-test

WORKDIR /tmp/work
ENTRYPOINT ["/bin/bash"]
