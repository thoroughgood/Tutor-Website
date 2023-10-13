#!/bin/bash

export PIPENV_DEFAULT_PYTHON_VERSION=3.10
export PIPENV_VENV_IN_PROJECT=true

python3 -m venv .venv
.venv/bin/pip3 install pipenv
.venv/bin/pipenv install

# will stop here if db push fails
.venv/bin/pipenv run prisma db push --schema prisma/schema.prisma || exit 1

# as suggested by https://docs.gunicorn.org/en/stable/deploy.html#using-virtualenv
.venv/bin/pipenv run python3 .venv/bin/gunicorn