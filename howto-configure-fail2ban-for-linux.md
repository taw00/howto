# HowTo Configure Fail2Ban for Linux

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

firewalld instructions have been expanded, clarified, and placed in their own HowTo. Please visit: <https://github.com/taw00/howto/blob/master/howto-configure-firewalld-for-linux-examples-laptop-and-server.md>

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
# You may have to edit this as user root, not just via sudo...
sudo nano /etc/fail2ban/jail.d/local.conf
```

Copy this, paste, then save...

```
[DEFAULT]
# Ban hosts for one hour:
bantime = 3600
# I'm really mad. Ban them for 24 hours:
#bantime = 86400

# Flip the comments here if you use iptables instead of firewalld
#banaction = iptables-multiport
banaction = firewallcmd-ipset

# Enable logging to the systemd journal
backend = systemd

# Email settings - Optional - Configure this only after send-only email is
# enabled and functional at the system-level.
#destemail = youremail+fail2ban@example.com
#sender = burner_email_address@yahoo.com
#action = %(action_mwl)s

[sshd]
enabled = true
```

> _For more about setting up "send-only email", read
[this](https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md)._


#### Enable `fail2ban` and reboot...

```
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
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
