#!/bin/bash

if [ -z "$DD_API_KEY" ]
then
  echo "Please set environment variable DD_API_KEY"
  exit 1
fi

python ../../../autotracing/parser.py . \
  -L /usr/local/opt/llvm/lib -I /usr/local/Cellar/curl/7.65.3/include -o traced

DD_API_KEY=${DD_API_KEY} docker-compose up \
  --build \
  --abort-on-container-exit \
  --exit-code-from dd-opentracing-cpp-example
docker rm dd-agent
