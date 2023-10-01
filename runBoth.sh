#!/bin/bash

cd backend

./runBackend.sh &

cd ../frontend

npm i
npm run dev
