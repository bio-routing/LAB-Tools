#!/bin/sh
ip addr add 169.254.100.0/32 dev lo
ip addr add 169.254.100.1/32 dev lo
ip addr add 169.254.200.0/32 dev lo
ip addr add 169.254.200.1/32 dev lo
docker rm -f bird-as65100
docker rm -f bird-as65200
docker run -d --privileged -p 169.254.100.0:179:179 -v $(pwd)/as65100.conf:/etc/bird/bird.conf --name "bird-as65100" pierky/bird
docker run -d --privileged -p 169.254.200.1:179:179 -v $(pwd)/as65200.conf:/etc/bird/bird.conf --name "bird-as65200" pierky/bird
