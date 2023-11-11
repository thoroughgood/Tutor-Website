FROM node:20
FROM python:3

WORKDIR /app
COPY . .

# Variables
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ARG poetry_version=1.6.1

# Build Stage
RUN pip install --upgrade pip
RUN python3 -m venv .venv
RUN .venv/bin/pip3 install -U pip setuptools
RUN .venv/bin/pip3 install poetry==$poetry_version
RUN yes | .venv/bin/poetry cache clear PyPI --all
RUN yes | .venv/bin/poetry cache clear _default_cache --all
RUN .venv/bin/poetry install

# Deploy Stage
# prisma cli must be installed in deploy and, 
# --accept-data-loss flag for db push is required otherwise it hangs
ENTRYPOINT [ "/bin/sh", "-c" , ".venv/bin/poetry run prisma db push --accept-data-loss && .venv/bin/poetry run .venv/bin/gunicorn" ]