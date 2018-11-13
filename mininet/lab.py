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

def tmux(pane, cmd):
    os.system("tmux -S /tmp/tmux.soccket send-keys -t '0:1.{}' C-z '{}' Enter"
            .format(pane, cmd))

def mtmux(host, pane, cmd):
    host.cmd("tmux -S /tmp/tmux.soccket send-keys -t '0:1.{}' C-z '{}' Enter"
            .format(pane, cmd))

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

        bird = self.addSwitch("bird1")
        bio = self.addSwitch("bio1")

        h1 = self.addNode("h1")
        h2 = self.addNode("h2")

        self.addLink(bird, h1)
        self.addLink(bio, h2)

        self.addLink(bird, bio)
        #self.addLink(bird, bio)
        #self.addLink(bio, bio)

def main():
    net = Mininet(topo=BGPTopo(), switch=Router)
    net.start()

    for router in net.switches:
        router.cmd("sysctl -w net.ipv4.ip_forward=1")
        router.waitOutput()

    bio = net.switches[0]
    bird = net.switches[1]

    print("bird: %s", bird)
    print("bio: %s", bio)

    h1 = net.hosts[0]
    h2 = net.hosts[1]

    # shell(bio, "bird -c ./as65200.conf -s ./as65200.ctl")
    shell(bio, "ip addr add dev lo 169.254.200.1")
    shell(bio, "ip addr add dev bio1-eth1 10.200.0.1/24")
    shell(bio, "ip addr add dev bio1-eth2 169.254.0.2/30")
    shell(bio, "sleep 1")
    shell(bio, "bio-rd > /var/log/bio-rd.log &")

    shell(bird, "ip addr add dev bird1-eth1 10.100.0.1/24")
    shell(bird, "ip addr add dev bird1-eth2 169.254.0.1/30")
    shell(bird, "sleep 1")
    shell(bird, "bird -c ./as65100.conf -s /tmp/as65100.ctl")

    # shell(bio, "~/src/bio-rd/bio-rd/bio-rd")
    #shell(bio, "ip addr add dev bio3-eth1 10.300.0.1/24")
    #shell(bio, "ip addr add dev bio3-eth2 169.254.0.2/30")

    # Hosts
    shell(h1, "ip addr add dev h1-eth0 10.100.0.2/24")
    shell(h1, "ip addr del dev h1-eth0 10.0.0.1/8")
    shell(h1, "ip route add 0.0.0.0/0 via 10.100.0.1")
    shell(h1, "ip route del 10.100.0.0/24")

    shell(h2, "ip addr add dev h2-eth0 10.200.0.2/24")
    shell(h2, "ip addr del dev h2-eth0 10.0.0.2/8")
    shell(h2, "ip route add 0.0.0.0/0 via 10.200.0.1")
    shell(h2, "ip route del 10.200.0.0/24")

    log("Spawn tmux sessions")
    #mtmux(bio, 1, "tail -f /var/log/bio-rd.log")
    tmux(2, "sudo birdc -s /tmp/as65100.ctl")

    CLI(net)
    net.stop()

    os.system("killall bird")
    os.system("killall bio-rd")

if __name__ == "__main__":
    os.system("killall bird")
    os.system("killall bio-rd")
    main()

