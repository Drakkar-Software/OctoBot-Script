FROM node:22-slim AS frontend

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY octobot_script/resources/report/ octobot_script/resources/report/
COPY vite.config.ts tsconfig*.json ./
RUN npm run build

FROM python:3.13-slim-bullseye AS base

WORKDIR /app

# requires git to install requirements with git+https
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git gcc binutils

COPY . .
COPY --from=frontend /app/octobot_script/resources/report/dist/ octobot_script/resources/report/dist/

RUN pip3 install --no-cache-dir -U setuptools wheel pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && python3 setup.py install

ENTRYPOINT ["bash"]
