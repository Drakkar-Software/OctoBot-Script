FROM python:3.10-slim-buster AS base

WORKDIR /app

# requires git to install requirements with git+https
# Update to debian archive from https://gist.github.com/ishad0w/6ce1eb569c734880200c47923577426a
RUN echo "deb http://archive.debian.org/debian buster main contrib non-free" > /etc/apt/sources.list \
    && echo "deb http://archive.debian.org/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://archive.debian.org/debian buster-backports main contrib non-free" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential git gcc binutils

COPY . .

RUN pip3 install --no-cache-dir -U setuptools wheel pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && python3 setup.py install

ENTRYPOINT ["bash"]
