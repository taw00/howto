# HowTo Do Fun Things with SSH Tunnels

SSH is short for "secure shell". SSH is used to "log in" to a remote system
through a secure communication channel. So, for example, if you have a remote
system, "x.y.z", and you are user, "todd" on that system, you can log into (ssh
into) that machine with a simple command: `ssh todd@x.y.z`. 

This establishes a secure communication channel between your local system and
that remote system. SSH can be leveraged to "tunnel" other data through that
secure communication channel. In fact, you can tell SSH to take the data coming
from a port on the remote machine through the tunnel to the local machine and
have it expressed through a local port of your choosing. This is called "port
forwarding" through an "ssh tunnel".

For example, if I had an application on the remote system that uses port 9997
to communicate. I can map a port on my local machine to that remote port 9997.

Why would I want to do this? Here are a few use cases...

* Maybe your corporate network administrators disallow connecting to the
  outside world except through SSH (fairly common actually)
* Maybe you don't want that remote machine exposing its port to the outside
  world.
* Securing a normally insecure REST API by controlling access via SSH.


So, how do we do this? Well, first, you really need to create an SSH keypair
so that you are not always typing a password every time you log into a remote
machine. 

But before we begin, you really need to create SSH keys to access a remote
system. Do that first and them come back to this howto: [HowTo Create and Use SSH Keys](https://github.com/taw00/howto/blob/master/howto-ssh-keys.md).

On to some examples...


## Access Cockpit through an SSH Tunnel

Cockpit is an excellent web application that enables some basic administration
and introspection of your linux systems. Learn more here:
<http://cockpit-project.org/> and <http://www.tecmint.com/cockpit-monitor-multiple-linux-servers-via-web-browser/>

Cockpit is a great tool, but it is a web-application which means you have to
open up a port (9090 by default) in order to access it directly.

Instead, let's "port forward" Cockpit's webapp interface through SSH so we can
firewall off that port from the outside world. How do I "firewall off that
port"? You can read about that here:
[HowTo Configure FirewallD](https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md),

Normally, you would access your server's Cockpit dashboard by browsing to the
remote server...

`https://<remote-server-ip-address>:9090`

For this example, I want to look at that remote server... locally. I
want to view it from this local browser link: 

`https://127.0.0.1:9091`

I picked the local port 9091 because I don't want it to conflict with my local
machine's instance of Cockpit which is already using port 9090.


* Turn off any firewall rules granting access from the outside world

SSH into the remote system...

```
ssh username@<remote-ip-address>
```

```
sudo firewall-cmd --permanent --remove-service cockpit
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
# Also remove any rich rules you may have configured for cockpit
```

* Make sure Cockpit is running

```
sudo systemctl status cockpit.socket
# If "inactive"...
sudo systemctl start cockpit.socket
sudo systemctl enable cockpit.socket
```

And then logout...

```
logout
```


* Set things up so that you "forward" cockpit's port, 9090.

This is called
["remote SSH port forwarding"](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding).

You create a remote SSH port forward from the machine local to you (my laptop
for example).

```
# Create a tunnel from your local 9091 port to the remote machine's 9090 port
ssh -L 9091:127.0.0.1:9090 <username>@<remote-ip-address> -N
```

What this says is...

  - Create an SSH tunnel to a remote system: `<username@remote-ip-address>`
  - Then pipe the results of its own `9090` content (cockpit) as if you were
    local `127.0.0.1`
  - And bind that system and port to our local `-L` port `9091`
  - That `-N` just terminates the SSH call and disallows any commands to be
    executed through SSH.
  - Note, if you run into trouble you can append `-v` 's to the command (up to
    three) to see verbose debugging information.

Now just browse to <https://127.0.0.1:9091> ... You will be viewing the remote
systems's Cockpit dashboard as if you were local to that machine. MAGIC!



## Other fun things...

(to be added)

