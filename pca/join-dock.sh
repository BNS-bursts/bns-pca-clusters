#!/bin/bash -x
docker exec -i  -u $(id -u):$(id -g) -t pca_session /bin/bash
