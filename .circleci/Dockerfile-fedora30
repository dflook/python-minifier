# This file should be pushed to danielflook/python-minifier-build:fedora30-<date>
FROM fedora:30

# CircleCI required tools
RUN dnf install -y \
      git \
      openssh \
      tar \
      gzip \
      gpg \
      ca-certificates \
 && dnf update -y

# Python versions
RUN dnf install -y \
      python26 \
      python27 \
      python34 \
      python35 \
      python36 \
      python37 \
      pypy \
      pypy3 \
      python2-test \
      python3-test

RUN dnf install -y \
      @development-tools \
      findutils \
      zlib-devel \
      bzip2-devel \
      ncurses-devel \
      gdbm-devel \
      openssl-devel \
      sqlite-devel \
      tk-devel \
      libuuid-devel \
      readline-devel \
      libnsl2-devel \
      xz-devel \
      libffi-devel \
      wget

RUN git clone https://github.com/python/cpython.git \
 && cd cpython \
 && git checkout 3.8 \
 && ./configure \
 && make \
 && make altinstall \
 && cd .. \
 && rm -rf cpython

WORKDIR /tmp/work
ENTRYPOINT ["/bin/bash"]
