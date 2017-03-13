# HowTo do fun things with SSH tunnels

SSH tunneling allows you to do a number of things you would not normally be
able to do remotely. I.e., You can allow SSH to have access to a remote server
(secure by definition) and serve things "locally" or via "localhost" to that
machine, but then piped through the tunnel to a remote system. I think this
will be more apparent with examples.

## Display Cockpit Data through an SSH Tunnel

I.e., Let's "port forward" Cockpit's webapp interface through SSH so we can
firewall off that port from the outside world.

If you have cockpit available to the outside world via [firewall
settings](https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md),
you can turn off outside access to that port if you are going to use an SSH
tunnel instead.

In this example, instead of having to browse to the remote server...

`https://<remote-server-ip-address>:9090`

...to view it's Cockpit dashboard, I want to have it funneled locally, for
example...

`https://127.0.0.1:9091`

I picked port 9091 because I don't want it to conflict with my local machine's
instance of Cockpit.


* Set up effortless SSH

HowTo for SSH key generation is not yet written. In the meantime,
[these are pretty good instructions](https://www.vultr.com/docs/how-do-i-generate-ssh-keys).

* SSH into the remote system...

```
ssh username@<remote-ip-address>
```

* Turn off the firewall rule granting access to the outside world

```
sudo firewall-cmd --permanent --remove-service cockpit
sudo firewall-cmd --reload
```

* Make sure Cockpit is running

```
sudo systemctl status cockpit.service
# If "inactive"...
sudo systemctl start cockpit.service
sudo systemctl enable cockpit.service
```

* Instead set things up so that you funnel cockpit's port, 9090.

This is called
["remote SSH port forwarding"](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding).

```
# If you are still SSHed into the remote system, exit now. You do this on your
# local machine. Or just open a new local terminal window. Then...
# Create a tunnel from your 9091 port to the remote machine's 9090 port
ssh -L 9091:127.0.0.1:9090 <username>@<remote-ip-address> -N
```

What this says is...

  - Create an SSH tunnel to a remote system: `<username@remote-ip-address>`
  - Then pipe the results of its own `9090` content (cockpit) as if you were
    local `127.0.0.1`
  - And plumb that system and port to our local `-L` port `9091`
  - That `-N` just terminates the SSH call and disallows any commands to be
    executed.
  - Note, if you run into trouble you can append `-v` 's to the command (up to
    three) to see verbose debugging information.

Now just browse to `https://127.0.0.1:9091` ... You will be viewing the remote
systems's Cockpit dashboard as if you were local to that machine. MAGIC!



## Other fun things...

(to be added)

