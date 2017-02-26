# Configure FirewallD and Fail2Ban for Linux

Whenever you expose a server to the wilds of the internet, it becomes vulnerable to attack.
If this is a webserver, ports 443 and 80 are open to attack. SSH? Of course you ssh in, that
is open to attack.

This document will get you started on configuring some basic firewall rules to help mitigate
against some of the more obvious problems, like brute-force DOS and trimming down the attack
surface by only having the minimal ports open.

We'll examine FirewallD and Fails2ban. FirewallD manages communication coming and going from
server. Fails2ban looks for oddities in how folks are attempting to access and adjusts firewall
rules on the fly to squelch misbehavior.

---

## FirewallD

_Note: Firewall rules can be a complicated topic. These are bare bones
git-er-done instructions. You may want to investigate further refinement,
though this will get you well on your way to a better protected system._

#### Install `firewalld`

```
# If Fedora...
sudo dnf install -y firewalld # Probably already installed
# If CentOS or RHEL...
sudo yum install -y firewalld # Probably already installed
# If Debian or Ubuntu
sudo apt install -y firewalld
```

#### Mask `iptables`

`iptables` and `firewalld` don't mix. Make sure they don't &mdash; "mask" `iptables`
(assuming it is installed)...

```
sudo systemctl disable iptables.service
sudo systemctl mask iptables.service
```

Note. If you end up ditching using `firewalld` and want to go back to
`iptables`...

```
sudo systemctl disable firewalld.service
sudo systemctl unmask iptables.service
sudo systemctl mask firewalld.service
```

I leave it as an exercise to the reader as to how to enable and work with
`iptables`.

#### Configure `firewalld`

```
# Is firewalld running? If not, turn it on
sudo firewall-cmd --state
sudo systemctl start firewalld.service
```

```
# Enable firewalld to start upon boot
sudo systemctl enable firewalld.service
```

```
# Determine what the default active zone is.
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-active-zone
```

```
# Take a look at the configuration as it stands now.
sudo firewall-cmd --list-all
```

Whatever that default zone is, that is the starting conditions for your
configuration. For this example, I am going to demonstrate how to edit my
default configuration on my Fedora Linux system: FedoraServer. You _could_
create your own zone definition, but for now, we will be editing the
configuration that is in place.

FedoraServer usually starts with ssh, dhcp6-client, and cockpit opened up by
default.  I want ssh. But dhcpv6 should probably be unneccessary, and cockpit
is something only used intermittently. To be explicit, I am going to add ssh
(though probably already an added service) and removing dhcpv6 and cockpit. 

You can see what other services are available with: `firewall-cmd get-services`

```
# Add and remove base services.
sudo firewall-cmd --permanent --add-service ssh
sudo firewall-cmd --permanent --remove-service dhcpv6-client
#sudo firewall-cmd --permanent --add-service cockpit
sudo firewall-cmd --permanent --remove-service cockpit
```

You can see what other services are available with: `firewall-cmd get-services`

You can look through one of the built in service files to determine exactly what
that service is all about: Browse directory `/usr/lib/firewalld/services`

If you want to add your own service for your own specialized application,
just copy a similar service from `/usr/lib/firewalld/services/` to `/etc/firewalld/`,
rename it, and edit it there.Then you can add it to a firewalld zone definition
at will.

```
# My own service, which is defined in /etc/firewalld/t0ddapp.xml It uses ports 9997!
sudo firewall-cmd --permanent --add-service t0ddapp

# I also have a random other application that needs to have port 9999 open, but only for
# TCP traffic.
#sudo firewall-cmd --permanent --add-port=9999/tcp
```

Let's rate limit traffic to those ports to reduce abuse. SSH and cockpit, if
those services were added really need to be rate limited. You would probably
want to rate limit 80 and 443, for example, if this were a webserver (but using
more liberal values).

_Note: It does not hurt to leave in the cockpit rate limiting. If you turn on
cockpit in the future, the rule will be already enabled._

```
# Rate limit incoming ssh and cockpit (if configured) traffic to 10 requests per minute
sudo firewall-cmd --permanent --add-rich-rule='rule service name=ssh limit value=10/m accept'
sudo firewall-cmd --permanent --add-rich-rule='rule service name=cockpit limit value=10/m accept'
sudo firewall-cmd --permanent --add-rich-rule='rule service name=t0ddapp limit value=5/s accept'
sudo firewall-cmd --permanent --add-rich-rule='rule service name=9999 limit value=20/s accept'
```

We're done with the configuration! That --permanent switch in those commands
saved the changed configuration, but it didn't enable them yet. We need to do a
reload for that to happen.

```
# did it take?
sudo firewall-cmd --reload
sudo firewall-cmd --state
sudo firewall-cmd --list-all
```

That's it! Not too hard, yet very powerful.

#### Some references:

* FirewallD documentation: <https://fedoraproject.org/wiki/Firewalld>
* Rate limiting as we do above: <https://www.rootusers.com/how-to-use-firewalld-rich-rules-and-zones-for-filtering-and-nat/>
* More on rate limiting: <https://serverfault.com/questions/683671/is-there-a-way-to-rate-limit-connection-attempts-with-firewalld>
* And more: <https://itnotesandscribblings.blogspot.com/2014/08/firewalld-adding-services-and-direct.html>
* Interesting discussion on fighting DOS attacks on http: <https://www.certdepot.net/rhel7-mitigate-http-attacks/>
* Do some web searching for more about firewalld

---

## Fail2Ban

Fail2ban analyzes log files for folks trying to do bad things on your system.
It doesn't have a lot of breadth of functionality, but it can be very
effective, especially against folks poking SSH.

#### Install `fail2ban`...

```
# If Fedora...
sudo dnf install -y fail2ban fail2ban-systemd
# If CentOS or RHEL
sudo yum install epel-release # if not already installed
sudo yum install -y fail2ban fail2ban-systemd
# If Debian or Ubuntu
sudo apt install -y fail2ban
```

If you are not using FirewallD, and instead are using IPTables for your
firewall, uninstall fail2ban-firewalld (for the Red Hat-based systems only).

```
sudo dnf remove -y fail2ban-firewalld # Fedora
sudo yum remove -y fail2ban-firewalld # CentOS or RHEL
```

#### Configure `fail2ban`...

Edit `/etc/fail2ban/jail.d/local.conf` _(Optionally `/etc/fail2ban/jail.local`
instead)_

```
sudo nano /etc/fail2ban/jail.d/local.conf
```

Copy this, paste, then save...

```
[DEFAULT]
# Ban hosts for one hour:
bantime = 3600
# I'm really mad. Ban them for 24 hours (the default):
#bantime = 86400

# Flip the comments here if you use iptables instead of firewalld
#banaction = iptables-multiport
banaction = firewallcmd-ipset

# Enable logging to the systemd journal
backend = systemd

[sshd]
enabled = true
```

#### Enable `fail2ban` and reboot...

_Note: The first time I attempted to start fail2ban &mdash; `sudo systemctl
start fail2ban` &mdash; a socket did not get created correctly until I
rebooted. I am not sure why._

```
sudo systemctl enable fail2ban
sudo reboot
```

#### Monitor / Analyze

Watch the IP addresses slowly pile up by occassionally looking in the SSH jail...

```
sudo fail2ban-client status sshd
```

Also watch...

```
sudo journalctl -u fail2ban.service -f
```

...and...

```
sudo tail -F /var/log/fail2ban.log 
```

#### Reference:

* <https://fedoraproject.org/wiki/Fail2ban_with_FirewallD>
* <https://en.wikipedia.org/wiki/Fail2ban>
* <http://www.fail2ban.org/>

---

## Done!

Good luck! Comments and feedback to <t0dd@protonmail.com>
