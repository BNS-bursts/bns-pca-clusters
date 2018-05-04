#!/bin/bash -x
docker run \
    -it -u $(id -u):$(id -g) \
    --rm --name pca_session \
    -e DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e BNSCLUSTERS_PREFIX="/work/BNS-bursts/bns-pca-clusters"\
    -v /home/jclark/Projects:/work \
    -v /home/jclark/Projects/BNS-bursts/bns-pca-clusters/pca:/utils \
    -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro \
    -w /work/BNS-bursts/bns-pca-clusters/pca -p 8888:8888 jclarkastro/pmns-dev
