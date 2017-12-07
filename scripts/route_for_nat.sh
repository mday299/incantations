#!/bin/bash

#TODO: usage statement
#TODO: options
#TODO: notice when I'm missing command line args

#TODO: option to do this to a remote ODroid rather than have to login via ssh fifirst

#argument is the ip of the gateway

cmds="sudo route add default gw $1"

#TODO: make this conditional with an option
cmds="$cmds; sudo killall unattended-upgr; sudo apt remove -y unattended-upgrades"

#130.207.244.251
#find with nmcli device show <device> | grep DNS
cmds="$cmds; sudo echo 'nameserver $2' >> /etc/resolv.conf"

#TODO: -optionally allow adding a second DNS server

#OPTION1 - local
#cmds

#OPTION2 - remote
#TODO: need to specify username and IP from command line
ssh root@192.168.90.101 "$cmds"

#TODO: make this finaal ssh login optional
#ssh root@192.168.90.101
