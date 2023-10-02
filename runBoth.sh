#!/bin/bash

cd backend

./runBackend.sh &
pid1=$!

cd ../frontend

npm i
npm run dev &
pid2=$!

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
trap "echo finished running both" SIGINT
wait "$pid1" "$pid2" 
