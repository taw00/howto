#!/usr/bin/bash

printf "specpatternd\n"
printf "The simple, demonized version of specpattern.\n"
printf "To make it end, you will have to 'killall specpatterd' or, if running\n"
printf "as a service, 'sudo systemctl stop specpatternd.service'\n"

/usr/share/specpattern/specpattern-process.sh &

