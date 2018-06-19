#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel
from mininet.util import dumpNodeConnections, quietRun, moveIntf
from mininet.cli import CLI
from mininet.node import Switch, OVSKernelSwitch

from subprocess import Popen, PIPE, check_output
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os
import termcolor as T
import time

setLogLevel('info')

def log(s, col="green"):
    print T.colored(s, col)

def shell(host, cmd):
    host.cmd(cmd)
    host.waitOutput()

class Router(Switch):
    """
    Defines a new router that is inside a network namespace so that the
    individual routing entries don't collide.

    """
    ID = 0
    def __init__(self, name, **kwargs):
        kwargs['inNamespace'] = True
        Switch.__init__(self, name, **kwargs)
        Router.ID += 1
        self.switch_id = Router.ID

    @staticmethod
    def setup():
        return

    def start(self, controllers):
        pass

    def stop(self):
        self.deleteIntfs()

    def log(self, s, col="magenta"):
        print T.colored(s, col)


class BGPTopo(Topo):
    def __init__(self):
        super(BGPTopo, self).__init__()

        r1 = self.addSwitch("R1")
        r2 = self.addSwitch("R2")

        h1 = self.addNode("H1")
        h2 = self.addNode("H2")

        self.addLink(r1, h1)
        self.addLink(r2, h2)
        self.addLink(r1, r2)

def main():
    os.system("killall bird")

    net = Mininet(topo=BGPTopo(), switch=Router)
    net.start()

    for router in net.switches:
        router.cmd("sysctl -w net.ipv4.ip_forward=1")
        router.waitOutput()

    shell(net.switches[0], "bird -c ./as65100.conf -s ./as65100.ctl")
    shell(net.switches[0], "ip addr add dev R1-eth1 10.100.0.1/24")
    shell(net.switches[0], "ip addr add dev R1-eth2 169.254.0.1/30")

    shell(net.switches[1], "bird -c ./as65200.conf -s ./as65200.ctl")
    shell(net.switches[1], "ip addr add dev R2-eth1 10.200.0.1/24")
    shell(net.switches[1], "ip addr add dev R2-eth2 169.254.0.2/30")

    shell(net.hosts[0], "ip addr add dev H1-eth0 10.100.0.2/24")
    shell(net.hosts[0], "ip route add 0.0.0.0/0 via 10.100.0.1")
    shell(net.hosts[0], "ip route del 10.100.0.0/24")
    shell(net.hosts[0], "ip route del 10.0.0.0/8")

    shell(net.hosts[1], "ip addr add dev H2-eth0 10.200.0.2/24")
    shell(net.hosts[1], "ip route add 0.0.0.0/0 via 10.200.0.1")
    shell(net.hosts[0], "ip route del 10.200.0.0/24")
    shell(net.hosts[1], "ip route del 10.0.0.0/8")

    CLI(net)
    net.stop()

    os.system("killall bird")

if __name__ == "__main__":
    main()

