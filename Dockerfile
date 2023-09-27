FROM python:3.10-slim-buster AS base

WORKDIR /pro

COPY . .

RUN pip3 install --no-cache-dir wheel \
    && pip3 install --no-cache-dir -r requirements.txt \
    && python3 setup.py install

ENTRYPOINT ["bash"]
