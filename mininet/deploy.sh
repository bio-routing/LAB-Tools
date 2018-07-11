#!/bin/bash -x
cd $GOPATH/src/github.com/bio-routing/bio-rd/
bazel build //:bio-rd

scp $GOPATH/src/github.com/bio-routing/bio-rd/bazel-bin/linux_amd64_stripped/bio-rd vagrant:/usr/local/bin/
scp $HOME/src/bio-rd/LAB-Tools/mininet/* vagrant:~/src/bio-rd/LAB-Tools/mininet/

ssh vagrant "killall tail"
ssh vagrant "sudo killall lab.py"
ssh vagrant "tmux -S /tmp/tmux.soccket send-keys -t '0:1.3' C-z 'sudo ./lab.py' Enter"
