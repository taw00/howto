#!/usr/bin/bash

# Used in ExecStarPre= in the specpatternd.service definition file to check for
# minimally correct conditions. The message will land in the log files:
# journalctl -xe

if [ ! -e /etc/specpattern/specpattern.conf ]
then
	echo "\
...
specpatternd.service start failure due to unsatisfied pre-conditions.

Before running 'systemctl start specpatternd.service' for the very first time,
you have to populate the /etc/specpattern/specpattern.conf configuration file.

The purpose of this check is just to show what can be done as a pre-flight
check before running the systemd service.
...
"
	exit 1
fi
