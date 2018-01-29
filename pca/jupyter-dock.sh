#!/bin/bash -x
docker run \
    -it -u $(id -u):$(id -g) \
    --rm --name pca_session \
    -v /home/jclark/Projects:/work \
    -v /home/jclark/Projects/BNS-bursts/utils:/utils \
    -w /work pmns-dev #-p 8888:8888 pmns-dev
