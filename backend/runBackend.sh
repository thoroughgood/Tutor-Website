#!/bin/bash

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

# will stop here if db push fails
prisma db push --schema prisma/schema.prisma || exit 1

# as suggested by https://docs.gunicorn.org/en/stable/deploy.html#using-virtualenv
python3 .venv/bin/gunicorn

deactivate
