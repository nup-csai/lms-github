#!/bin/bash

CONTAINER_NAME="lms-shell"
IMAGE_NAME="krinkin/lmsh"



docker  rm -f ${CONTAINER_NAME}  2>/dev/null || true \
		&& docker run --rm --name ${CONTAINER_NAME} ${IMAGE_NAME} \
		 python3 /lmsh/lmsh.py "$@"


#docker exec -it ${CONTAINER_NAME} -rm --force-recreate bash
