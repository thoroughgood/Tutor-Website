FROM ubuntu
FROM node:18
FROM python:3

WORKDIR /app
COPY . .

# Generic python setup
RUN pip install --upgrade pip  
# No need to bother with venv with docker
RUN pip install -r requirements.txt
RUN prisma generate