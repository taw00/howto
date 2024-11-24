# HowTo Configure FirewallD for Linux<br />_(examples, a laptop and a server)_

> **TL;DR versions are towards the end of this document**

Firewalld is a mechanism to define firewall "zones" of rules that you then apply to network interfaces (rules that you assign to interfaces). An interface is something like `eth0`, `eth1`, `wlp1s0`, `ens3`.

FirewallD is a far FAR more user-friendly improvement over IPTables. It's important to understand that you create these zones (sets of rules) to be applied to network interfaces and not to your computer in general. You can create an infinite number of zones, but they are just that &mdash;rules&mdash; that have no purpose until an interface is assigned to them.

Zones are created and managed for `firewalld` (the systemd service) using `firewall-config` (a graphical application) or with the commandline (`firewall-cmd`). We will focus on the commandline here since I think it makes it easier to understand for instructional purposes. I encourage the reader to first apply a set of rules using the commandline and then browse the graphical application and see how the rules are laid own conceptually.

For my laptop, I want to `ssh` access enabled but throttled, but otherwise, packets to be dropped. For my servers, I want `ssh` access, but also other services depending on the purpose of the server: `https` and `http` for a webserver, maybe enable `cockpit`, and maybe some set of ports opened up to enable some other service over the network. For some services (for cockpit for example) we may prefer to use ssh tunnels instead. We'll discuss that later in this document.

Finally, service `fail2ban` nicely compliments your firewall configuration. Read more about that here: <https://github.com/taw00/howto/blob/master/howto-configure-fail2ban-for-linux.md>

## Preparation: Install `firewalld`

Odds are the firewalld service is already installed, though it may need to be enabled and started.
```shell
sudo systemctl enable firewalld.service
sudo systemctl start firewalld.service
```

_**If that worked, you don't have to do the rest of this section.**_

My examples were all done on Fedora, but they should work on any system that offers firewalld (most modern linuxes).

Is firewalld installed?
```shell
which firewall-cmd
```

Is the desktop application installed? Note that firewall-config is not used in this document.
```shell
which firewall-config
```

Install firewalld if necessary
```shell
# If Fedora or CentOS or RHEL . . .
sudo dnf install -y firewalld
# If Debian or Ubuntu . . .
sudo apt install -y firewalld
```

If you really want to, go ahead and add `firewall-config` to that install.

**Mask iptables**

iptables and firewalld don't mix, per ce. Make sure they don't — "mask" iptables (assuming it is installed)...

```shell
sudo systemctl disable iptables.service
sudo systemctl mask iptables.service
```

Note. If you end up ditching using firewalld and want to go back to iptables (if installed)...
```shell
# Don't do this if you want to use firewalld
sudo systemctl disable firewalld.service
sudo systemctl unmask iptables.service
sudo systemctl mask firewalld.service
```

I leave it as an exercise to the reader as to how to enable and work with iptables.

Configure firewalld
```shell
# Is firewalld running? If not, turn it on
sudo firewall-cmd --state
sudo systemctl start firewalld.service

# Enable firewalld to start upon boot
sudo systemctl enable firewalld.service
```

## Preparation: Set up a custom zone

List the active zones. I.e., the ones with a network interface associated to them. My laptop lists `wlp1s0` which is the WiFi interface, and it has the "FedoraWorkstation" zone associated to it. We'll create a new zone of rules and then switch the interface to that zone.

```shell
# Show the zones currently applying rules to active network interfaces
sudo firewall-cmd --get-active-zones
```

> **Confusion point: what if `--get-active-zones` returns nothing?**  
>
> I have seen behavior where no active zone is returned even though
> `firewall-cmd --list-all` returns information about a zone (i.e. the default,
> and presumably active zone. I'm not sure what is going on, but this may or
> may not be a bug.
>
> In this case, at the `--change-interface` step below, you will have to
> explicitely set the the interface that you see as the result of any network
> query program, like `ifconfig`. In my case, command `ifconfig` shows an
> interface of `ens3`.
>
> I think there is a bug here. Or at least some improvement needed. I have
> filed a bug/issue/inquiry on this:
> <https://github.com/firewalld/firewalld/issues/333>.


Create a new zone...

```shell
sudo firewall-cmd --permanent --new-zone=todds-laptop
```
**...or, if this is a server...**
```shell
sudo firewall-cmd --permanent --new-zone=todds-server
```

That new zone is queue up for inclusion, but not viewable by the runtime version of firewalld until it is restarted. Example...

```shell
# You will see it queued up for inclusion.
sudo firewall-cmd --permanent --get-zones

# But you won't see it here yet...
sudo firewall-cmd --get-zones

# Include it into the active roster...
sudo firewall-cmd --reload

# Now you see it as part of the runtime...
sudo firewall-cmd --get-zones
```

## Laptop example -- configure rules and apply to interface

_**Note that we already created the zone in the "Preparation: Set up a custom zone" section above.**_

For my laptop, most everything is commented out since it does not serve as a server to outside clients... except for ssh. Always have to have ssh. If you uncomment things like http/https or cockpit, that assumes you installed some httpd service (apache? nginx?) or cockpit. If not, leave those lines commented.

```shell
# It's unlikely that you do much with IPV6 but add this service to make IPv6
# work right...
sudo firewall-cmd --zone=todds-laptop --permanent --add-service=dhcpv6-client
sudo firewall-cmd --zone=todds-laptop --permanent --add-service=ssh
#sudo firewall-cmd --zone=todds-laptop --permanent --add-service=http
#sudo firewall-cmd --zone=todds-laptop --permanent --add-service=https
#sudo firewall-cmd --zone=todds-laptop --permanent --add-service=cockpit
```

DDOS attacks suck. Throttle bad actors. You can leave these uncommented. They simply are no-ops until the service is added.

```shell
# Limit a service in order to manage DDOS...
sudo firewall-cmd --zone=todds-laptop --permanent --add-rich-rule='rule service name=ssh accept limit value=10/m'
sudo firewall-cmd --zone=todds-laptop --permanent --add-rich-rule='rule service name=http accept limit value=10/s'
sudo firewall-cmd --zone=todds-laptop --permanent --add-rich-rule='rule service name=https accept limit value=10/s'
sudo firewall-cmd --zone=todds-laptop --permanent --add-rich-rule='rule service name=cockpit accept limit value=10/m'
```

> **About DROP versus REJECT targets.**<br />Firewalld will REJECT packets by default (--set-target=default or --set-target=REJECT). This means a packet is given the boot, but the system responds with a nice rejection notification. DROPped packets are simply dropped on the floor with no response back to the calling system. The connection will hang for them until they hit some timeout. For port-scanners walking all over your system, DROP is no better than REJECT. For some casual hacker though, it may slow them down. REJECT is a nicer cleaner response. _For your servers you want to use REJECT -- for your laptop, DROP is an option_ and brings me more satisfaction.

For my laptop, DROP!

```shell
sudo firewall-cmd --zone=todds-laptop --permanent --set-target=DROP
```

Reload `firewalld` and see all the changes!
```shell
# reload
sudo firewall-cmd --reload
# all the changes are in place
sudo firewall-cmd --zone=todds-laptop --list-all
# but since we haven't re-aligned the interface, we aren't using the zone yet...
sudo firewall-cmd --get-active-zones
```

**Associate these rules to our interface**
* `wlp1s0` is what my computer reported (yours may vary)
* to have it apply, we _may_ have to bounce the network service

```shell
#
# Do this to switch an interface to the new zone
# (only if you have an interface listed)
#
# change the interface association
sudo firewall-cmd --zone=todds-laptop --change-interface=wlp1s0

# still associated to FedoraWorkstation
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=wlp1s0

# bounce the network -- commented out; you may not have to do this
#sudo systemctl restart network

# now associated to todds-laptop
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=wlp1s0
```

Make 'todds-laptop' your default zone!

```shell
sudo firewall-cmd --set-default-zone=todds-laptop
sudo systemctl restart firewalld
# if fail2ban complains, you may have to stop that service first, then restart
# firewalld, then start fail2ban again
```

> Note that if there are any other interfaces associated to the previously
  default zone, they will move over to the new default zone (_may_ have to do
  another network bounce to make that happen, I am not sure, I haven't tested
  this)



## Server example -- configure rules and apply to interface

_**Note that we already created the zone in the "Preparation: Set up a custom zone" section above.**_

For this example, we are assuming this is a webserver, but also has another service at port 5001 available. We'll ssh tunnel to the cockpit service (I'll show how). This assumes you installed some httpd service (apache? nginx?) and cockpit. If not, comment those lines out.

```shell
# It's unlikely that you do much with IPV6 but add this service to make IPv6
# work right...
sudo firewall-cmd --zone=todds-server --permanent --add-service=dhcpv6-client
sudo firewall-cmd --zone=todds-server --permanent --add-service=ssh
sudo firewall-cmd --zone=todds-server --permanent --add-service=http
sudo firewall-cmd --zone=todds-server --permanent --add-service=https
# I have some specialized service that runs on ports 5001 and 5002, but doesn't
# have a service definition file with a human readable name...
sudo firewall-cmd --zone=todds-server --permanent --add-port=5001-5002/tcp
#sudo firewall-cmd --zone=todds-server --permanent --add-service=cockpit
```

DDOS attacks suck. Throttle bad actors. You can leave these uncommented. They simply are no-ops until the service is added. Note that you can add a rich rule even if the named service doesn't exist yet.

```shell
# Limit a service in order to manage DDOS...
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=ssh accept limit value=10/m'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=http accept limit value=10/s'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=https accept limit value=10/s'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=cockpit accept limit value=10/m'
# I have some specialized service that runs on ports 5001 to 5002, but doesn't
# have a service definition file with a human readable name...
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule family=ipv4 port port="5001-5002" protocol=tcp limit value=20/s accept'
```

_For your servers you want to use REJECT. Could use 'default' here instead of
 'REJECT', but REJECT is explicit._


```shell
sudo firewall-cmd --zone=todds-server --permanent --set-target=REJECT
```

Reload `firewalld` and see all the changes!
```shell
# reload
sudo firewall-cmd --reload
# all the changes are in place
sudo firewall-cmd --zone=todds-server --list-all
# but since we haven't re-aligned the interface, we aren't using the zone yet...
sudo firewall-cmd --get-active-zones
```

**Associate these rules to our interface**
* `eth0` is what my computer reported (yours may vary)
* to have it apply, we _may_ have to bounce the network service

```shell
#
# Do this to switch an interface to the new zone
# (only if you have an interface listed)
#
# change the interface association
sudo firewall-cmd --zone=todds-server --change-interface=eth0

# still associated to FedoraWorkstation (or probably FedoraServer or whatever)
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=eth0

# bounce the network -- commented out; you may not have to do this
#sudo systemctl restart network

# now associated to todds-server
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=eth0
```

Make 'todds-server' your default zone!

```shell
sudo firewall-cmd --set-default-zone=todds-server
sudo systemctl restart firewalld
# if fail2ban complains, you may have to stop that service first, then restart
# firewalld, then start fail2ban again
```

> Note that if there are any other interfaces associated to the previously
  default zone, they will move over to the new default zone (may have to do
  another network bounce to make that happen, I am not sure, I haven't tested
  this)

## SSH Tunneling to use cockpit from my laptop...

On my server, I installed and enabled cockpit...

**On the server:**
```shell
sudo dnf install cockpit
sudo systemctl enable cockpit.socket
sudo systemctl start cockpit.socket
```

Note that the port used by cockpit is 9090. Make sure it is not allowed via firewall...

```shell
sudo firewall-cmd --zone=todds-server --remove-service=cockpit
```

You should not be about to browse to that IP address from your laptop to that service: <https://[your-server-ip]:9090>

**Let's ssh tunnel to it instead!**

**On the laptop (assumption: you have ssh access to the server)**

```shell
ssh -L 9091:127.0.0.1:9090 <username@server-ip> -N
```

Now browse to your server's instance of cockpit from your laptop: <http://127.0.0.1:9091> or <http://localhost:9091>

Slick!

## I hope this was helpful...

Feedback and comments: `t0dd_at_protonmail.com`

## Resources

* Very general: <https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-using-firewalld-on-centos-7>
* All about `firewalld`: <https://fedoraproject.org/wiki/Firewalld?rd=FirewallD>
* Rich rules: <https://fedoraproject.org/wiki/Features/FirewalldRichLanguage>
* Why do we have to declare dhcpv6-client?: <https://unix.stackexchange.com/questions/176717/what-is-dhcpv6-client-service-in-firewalld-and-can-i-safely-remove-it#176773>
* DROP vs REJECT: <https://www.chiark.greenend.org.uk/%7Epeterb/network/drop-vs-reject>
* Rate limiting: <https://www.rootusers.com/how-to-use-firewalld-rich-rules-and-zones-for-filtering-and-nat/>
* More on rate limiting: <https://serverfault.com/questions/683671/is-there-a-way-to-rate-limit-connection-attempts-with-firewalld>
* And more: <https://itnotesandscribblings.blogspot.com/2014/08/firewalld-adding-services-and-direct.html>
* Interesting discussion on fighting DOS attacks on http: <https://www.certdepot.net/rhel7-mitigate-http-attacks/>
* SSH Tunneling: <https://github.com/taw00/howto/blob/master/howto-ssh-tunnel.md>
* Fail2Ban: <https://github.com/taw00/howto/blob/master/howto-configure-fail2ban-for-linux.md>
* Lots of HowTos: <https://github.com/taw00/howto>

---
---

## TL;DR - Laptop example in one pass...

**Assumptions:**
* firewalld is installed (see first section)
* `wlp1s0` is my computer's reported interface (via `--get-active-zones`)

```shell
sudo systemctl enable firewalld.service
sudo systemctl start firewalld.service
```

```shell
# -- CREATE NEW ZONE
# Show the zones currently applying rules to active network interfaces
sudo firewall-cmd --get-active-zones
# create a new zone...
sudo firewall-cmd --permanent --new-zone=todds-laptop
# include it into the active roster...
sudo firewall-cmd --reload

# --RULES
#   only ssh and it is rate limited. Everything else is DROPped
sudo firewall-cmd --zone=todds-laptop --permanent --add-service=dhcpv6-client
sudo firewall-cmd --zone=todds-laptop --permanent --add-service=ssh
sudo firewall-cmd --zone=todds-laptop --permanent --add-rich-rule='rule service name=ssh accept limit value=10/m'
sudo firewall-cmd --zone=todds-laptop --permanent --set-target=DROP

# reload
sudo firewall-cmd --reload

# all the changes are in place
sudo firewall-cmd --zone=todds-laptop --list-all

# --INTERFACE --> RULES
# (only do this if an interface is listed with '--get-active-zones')

# since we haven't re-aligned the interface, we aren't using the
# zone yet...
sudo firewall-cmd --get-active-zones
# associate...
sudo firewall-cmd --zone=todds-laptop --change-interface=wlp1s0
# bounce the network -- commented out; you may not have to do this
#sudo systemctl restart network
# check that the interface is now associated to todds-laptop
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=wlp1s0

# --SET NEW DEFAULT
# set todds-laptop as the new default zone
sudo firewall-cmd --set-default-zone=todds-laptop
#sudo systemctl stop fail2ban # --uncomment if installed and using
sudo systemctl restart firewalld
#sudo systemctl start fail2ban # --uncomment if installed and using
```

<div style="text-align: center; color: lightgrey;font-size: 200%;">&#11835;&#11835;&#11835;</div>

## TL;DR - Server example in one pass...

**Assumptions:**
* firewalld is installed (see first section)
* `eth0` is my computer's reported interface (via `--get-active-zones`)
* we are a webserver and have another specialized where we need access to ports 5001-5002

```shell
sudo systemctl enable firewalld.service
sudo systemctl start firewalld.service
```

```shell
# -- CREATE NEW ZONE
# Show the zones currently applying rules to active network
# interfaces
sudo firewall-cmd --get-active-zones
# create a new zone...
sudo firewall-cmd --permanent --new-zone=todds-server
# include it into the active roster...
sudo firewall-cmd --reload

# --RULES
#   various services and rate limited. Everything else is REJECTed
sudo firewall-cmd --zone=todds-server --permanent --add-service=dhcpv6-client
sudo firewall-cmd --zone=todds-server --permanent --add-service=ssh
sudo firewall-cmd --zone=todds-server --permanent --add-service=http
sudo firewall-cmd --zone=todds-server --permanent --add-service=https
sudo firewall-cmd --zone=todds-server --permanent --add-port=5001-5002/tcp

sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=ssh accept limit value=10/m'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=http accept limit value=10/s'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=https accept limit value=10/s'
sudo firewall-cmd --zone=todds-server --permanent --add-rich-rule='rule service name=cockpit accept limit value=10/m'
sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 port port="5001-5002" protocol=tcp limit value=20/s accept'

sudo firewall-cmd --zone=todds-server --permanent --set-target=REJECT

# reload
sudo firewall-cmd --reload

# all the changes are in place
sudo firewall-cmd --zone=todds-server --list-all

# --INTERFACE --> RULES
# (only do this if an interface is listed with '--get-active-zones')

# since we haven't re-aligned the interface, we aren't using the
# zone yet...
sudo firewall-cmd --get-active-zones
# associate...
sudo firewall-cmd --zone=todds-server --change-interface=eth0
# bounce the network -- commented out, you may not have to do this
#sudo systemctl restart network
# check that the interface is now associated to todds-server
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-zone-of-interface=eth0

# --SET NEW DEFAULT ZONE
# set todds-server as the new default zone
sudo firewall-cmd --set-default-zone=todds-server
#sudo systemctl stop fail2ban # --uncomment if installed and using
sudo systemctl restart firewalld
#sudo systemctl start fail2ban # --uncomment if installed and using
```
