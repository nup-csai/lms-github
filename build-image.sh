#!/bin/bash


docker build . -t   krinkin/lmsh:latest -f docker/Dockerfile.lmsh
docker build . -t krinkin/lmsapi:latest -f docker/Dockerfile.api

#docker push       krinkin/lmsh
#docker push       krinkin/lmsapi


