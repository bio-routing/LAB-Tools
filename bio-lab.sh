#!/bin/bash

ip addr add 169.254.255.255 dev lo

ip netns add AS65100
ip netns add AS65200

ip link add veth0 type veth peer name veth1
ip link set veth0 netns AS65100
ip netns exec AS65100 ip link set up dev veth0
ip netns exec AS65100 ip addr add 169.254.100.0/31 dev veth0
ip link set up dev veth1
ip addr add 169.254.100.1/31 dev veth1

ip link add veth2 type veth peer name veth3
ip link set veth3 netns AS65200
ip netns exec AS65200 ip link set up dev veth3
ip netns exec AS65200 ip addr add 169.254.200.1/31 dev veth3
ip link set up dev veth2
ip addr add 169.254.200.0/31 dev veth2

ip netns exec AS65100 bird -c as65100.conf -s as65100.ctl
ip netns exec AS65200 bird -c as65200.conf -s as65200.ctl


