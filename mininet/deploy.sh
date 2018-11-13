#!/bin/bash -xe

ssh vagrant "sudo killall lab.py || true"
ssh vagrant "sudo mn -c"

cd $GOPATH/src/github.com/bio-routing/bio-rd/examples/netlink

scp $GOPATH/src/github.com/bio-routing/bio-rd/examples/netlink/netlink vagrant:/usr/local/bin/bio-rd
scp $HOME/src/bio-rd/LAB-Tools/mininet/* vagrant:~/src/bio-rd/LAB-Tools/mininet/

ssh vagrant "tmux -S /tmp/tmux.soccket send-keys -t '0:1.3' C-z 'cd /home/vagrant/src/bio-rd/LAB-Tools/mininet' Enter"
ssh vagrant "tmux -S /tmp/tmux.soccket send-keys -t '0:1.3' C-z 'sudo ./lab.py' Enter"
