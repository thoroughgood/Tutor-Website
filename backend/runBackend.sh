#!/bin/bash

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

# will stop here if db push fails
prisma db push --schema ./schema.prisma || exit 1

python3 main.py

deactivate
