FROM node:20
FROM python:3

WORKDIR /app
COPY . .

# Generic python setup
RUN pip install --upgrade pip  
# we can just run the backend script for the rest
ENTRYPOINT [ "./runBackend.sh" ]