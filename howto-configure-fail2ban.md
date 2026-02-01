# HowTo Configure Fail2Ban for Linux

Firewalls and tools such as Fail2Ban help mitigate network attacks on your
system. For firewall specific instructions, please visit [this
link](https://github.com/taw00/howto/blob/master/howto-configure-firewalld-for-linux-examples-laptop-and-server.md).
Fail2Ban examines log activity looking for abusive actors and then takes action
on them by adjusting firewall rules on-the-fly as needed. Both services are
highly recommended for improving the security of a system. This document
focuses on Fail2Ban.

## Fail2Ban

Fail2ban analyzes log files for folks trying to do bad things on your system.
It doesn't have a lot of breadth of functionality, but it can be very
effective, especially against folks poking at SSH.

#### Install `fail2ban`...

```shell
# If Fedora...
sudo dnf install -y fail2ban fail2ban-systemd ipset
```
```shell
# If CentOS or RHEL
sudo dnf install epel-release # if not already installed
sudo dnf install -y fail2ban fail2ban-systemd ipset
```
```shell
# If Debian or Ubuntu
sudo apt install -y fail2ban ipset
```

If you are not using FirewallD, and instead are using IPTables (not recommended
in 2018) for your firewall rules management, uninstall fail2ban-firewalld (for
the Red Hat-based systems only).

```shell
# For iptable rules management only -- not recommended for most people
sudo dnf remove -y fail2ban-firewalld
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


#### Enable `fail2ban` and restart...

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

## Good luck!

Comments and feedback  
—Todd Warner <a href="https://forms.gle/ogCeqcdqNSogYkPU8">(google contact form)</a>
