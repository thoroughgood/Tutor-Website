FROM ubuntu
FROM python:3

WORKDIR /app
COPY . .

# Courtesy of https://stackoverflow.com/questions/25899912/how-to-install-nvm-in-docker/62838796#62838796 with some version changes
# nvm requirements
RUN apt-get update
RUN echo "y" | apt-get install curl
# nvm env vars
RUN mkdir -p /usr/local/nvm
ENV NVM_DIR /usr/local/nvm
# IMPORTANT: set the exact version
ENV NODE_VERSION v18.18.0
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION"
# add node and npm to the PATH
ENV NODE_PATH $NVM_DIR/versions/node/$NODE_VERSION/bin
ENV PATH $NODE_PATH:$PATH
RUN npm -v
RUN node -v

# Generic python setup
RUN pip install --upgrade pip  
# No need to bother with venv with docker
RUN pip install -r requirements.txt
RUN prisma generate