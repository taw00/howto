#!/usr/bin/bash

printf "Starting specpatternd -- the simple, demonized version of specpattern.\n"
printf "To make it end, you will have to 'killall specpatterd' or, if running\n"
printf "as a service, 'sudo systemctl stop specpatternd'\n"

#$(/usr/share/specpattern/specpattern-process.sh | systemd-cat -t specpatternd) &
/usr/share/specpattern/specpattern-process.sh &

