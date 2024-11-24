# HowTo Install Syncthing on a Headless Linux Server

## Introduction

[Syncthing](https://syncthing.net/) is an application that allows you to share
a directory tree between machines both simply and securely.

Headless Server is a system where you don't have access to a GUI frontend. For
example, a linux VPS share running on some service, like Vultr.com.

> To get a minimal headless system up and running, check out
  [this howto](https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md).

This document doesn't explain how to configure or use Syncthing. It's purpose is to help you get it running on a minimalistic linux server so it can act as a storage hub. And if that service is a VPS cloud share, it can act as a "cloud storage" hub.

### The motivation

My household consists of three computers running linux, one computer running
MacOS, and one computer running ChromeOS. We also have two Android phones
between us. 

We often pass around files (documents, video snippets, images, whatever).
Syncthing makes this simple. Synthing is a relatively simple and lightweight
application that runs on all of those devices I mentioned above and enables
secure, peer-to-peer sync of designated directory (folder) trees between them.
Example, if I share my `Documents/` folder with my wife, all I have to do is
copy `family-xmas-list.md` to that folder and it will show up on her machine.
Simple and it was never shared with some corporate cloud.

To install and configure Syncthing on your normal desktops, check out this
article:
[PCWorld Article: "How to Use Syncthing to Sync Files without the Cloud]
(https://www.pcworld.com/article/2048298/how-to-use-syncthing-to-sync-files-without-the-cloud.html)
and also the [docs at Syncthing.net](https://docs.syncthing.net/).

In the past we used Proton Drive for sensitive items and for everything else
Google Drive, Dropbox, Box, etc. These are fine, but (a) we'd be dependent on an
external service, (b) their promises of security (Proton Drive, I'm convinced,
is secure though), and111.222.333.4 (c) sometimes use of those services is not as simple as
copying files to and from a shared directory tree. Nextcloud is also an option, but it is not quite as dead simple and it _requires_ a cloud instance, whereas Syncthing does not.

> _Note, Keybase, via kbfs, used to be an option, but that implementation is
slow and horrendously prone to lockups, and since Keybase was sold to Zoom, kbfs
has been relegated to maintenance mode with the threat of shutdown always
looming. I love to use Keybase's git repositories though._

Syncthing is secure, almost dirt simple to set up, and, IMHO, it's elegant. With Syncthing + a linux VPS instance, we can pass around files no matter where we are in the world and no matter how seperated our computers are.

#### Why set it up on a VPS server?

Syncthing is a peer-to-peer service. If two machines are not on the same network
(like at my house), then they cannot share files between them until those
machines rejoin the shared network. A relatively cheap VPS accessible to the
public internet though can serve as that bridge between networks and therefore
enable sync between machines no matter where they are located.

Security? On a public network? Syncthing is secure, though no piece of software
is free of defects. And a lot depends on how well you lock down that server in
general. Therefore, I would recommend not using it to sync folders containing
more sensitive information. For that kind of stuff, use Syncthing to sync those
more sensitive folders between your local machines only and just deal with the
fact that they can only sync if they are on the same network.

---

## Let's get to work!

Step one: set up and secure a minimal server somewhere that is publicly
accessible. I like [Vultr](vultr.com). Need help?
[This can get you started.](https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md).

### Values used for purposes of this demonstration

- remote system name: `headless01`
- remote system IP: `203.0.113.5`
- remote linux username: `todd`
- remote dedicated linux username to run Syncthing: `syncthinguser`  
- ssh identity file (public key): `pubkey-headless01-rsa`
- Syncthing in-app username: `syncthinguser`
- Syncthing in-app password: `the syncthinguser is syncing w/ the syncthing service`
- Paths if using the `systemd` service and the `syncthinguser` user:
  - User Home: `/home/syncthinguser`
  - Configuration Directory: `/home/syncthinguser/.local/state/syncthing`
  - Configuration File: `/home/syncthinguser/.local/state/syncthing/config.xml`
  - Device Certificate: `/home/syncthinguser/.local/state/syncthing/cert.pem`
  - `/home/syncthinguser/.local/state/syncthing/key.pem`
  - GUI / API HTTPS Certificate: 
    `/home/syncthinguser/.local/state/syncthing/https-cert.pem` and 
    `/home/syncthinguser/.local/state/syncthing/https-key.pem`
- Database Location: `/home/syncthinguser/.local/state/syncthing/index-v0.14.0.db`
- Log File: (undefined or `journalctl -u syncthing@syncthinguser.service`)
- GUI Override Directory: `/home/syncthinguser/.local/state/syncthing/gui`

### Do this on the headless server, headless01

Login as normal login user with sudoers privledges. In this example `todd`.

#### Install syncthing and firewalld

```bash
sudo dnf install syncthing firewalld -y
```

#### Configure firewalld for Syncthing

For more expansive info about firewalld (and fails2ban): <https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md>

```bash
# Turn on and enable firewalld if not already done...
sudo firewall-cmd --state
sudo systemctl start firewalld.service
sudo systemctl enable firewalld.service

# If you had custom zoning set, remember to add --zone=<zonelabel> to the
# configuration commands, though if the zone is configured to be the default,
# things should "just work"
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=<zonelabel> --list-all

# allow the syncthing service, but DO NOT allow the GUI service to be exposed
# to the internet. We use an SSH tunnel to access that
sudo firewall-cmd --add-service=syncthing --permanent
#sudo firewall-cmd --add-service=syncthing-gui --permanent
sudo firewall-cmd --reload
```

#### Allow Syncthing's webUI interface to be SSH forwarded

```bash
sudo bash -c 'echo "
# To enable Syncthing
AllowTcpForwarding yes
" >> /etc/ssh/sshd_config''

sudo systemctl restart sshd
```

#### Create the `syncthinguser` user

This is a normal linux user that is only used to manage this Syncthing service.
You could use the first normal linux user (`todd` in this example) but is it
good practice to somewhat isolate activities on a server versus a desktop
environment. The `todd` user is essentially the system management user.

```bash
sudo useradd syncthinguser
# optional …
sudo passwd syncthinguser
```

#### Set up and run the systemd service

The pattern for this command is:
`sudo systemctl <command> syncthing@<linuxusername>.service`

That linuxusername is the name of the user who will be running syncthing and in
this case, we created a user to do just that: `syncthinguser`

```bash
sudo systemctl enable syncthing@syncthinguser.service
sudo systemctl start syncthing@syncthinguser.service
```

---

### On the workstation

Configure and connect an SSH Tunnel, then browse to the remote Syncthing service to use and configure that remote Syncthing instance. There are two methods to manage this:

1. Running `autossh` / `ssh` in the raw from the commandline (or via a script)
2. Running `autossh` / `ssh` that calls an `~/.ssh/config` connection definition

```bash
sudo dnf install autossh -y
```

#### Raw and scripted call to `autossh` / `ssh` method

Just run it . . .

```bash
#ssh -f -N -L 58384:127.0.0.1:8384 todd@${headless_ip}
autossh -f -M 0 -N -L 58384:127.0.0.1:8384 todd@${headless_ip}
```

But if we go this route, I prefer embedding it in a script . . .

```bash
echo "\
#!/usr/bin/bash

headless_hostname='headless01'
headless_ip='203.0.113.5'

# Note, for the SSH tunnel you generally have to do 127.0.0.1 and not localhost.
echo '# SSH Tunneling to Syncthing web service on ${headless_hostname} (${headless_ip})'
echo '  ssh -f -N -L 58384:127.0.0.1:8384 todd@${headless_ip}'

#ssh -f -N -L 58384:127.0.0.1:8384 todd@${headless_ip}
autossh -f -M 0 -N -L 58384:127.0.0.1:8384 todd@${headless_ip}

echo '# Now, browse to http://localhost:58384'
" > ssh-tunnel-syncthing-at-headless01.sh
```

Now, run the script . . .

```bash
. ./ssh-tunnel-syncthing-at-headless01.sh
```

If you can browse to <http://localhost:58384> without issue, then you can
slap that script into your `.bash_profile` so it runs at initial login . . .

```bash
echo "
# SSH Tunnel to …
# Syncthing administration service running at the headless01 server
echo \"Launching SSH tunnel to Synthing admin on headless01 (203.0.113.5)\"
/path/to/ssh-tunnel-syncthing-at-headless01.sh
echo \"Now, browse to http://127.0.0.1:58384\"" >> ~/.bash_profile
```

#### SSH Config method (more professional, IMHO)

Add this stanza to `~/.ssh/config` …

```bash
echo "\
host tunnel_headless_syncthing
    Hostname 203.0.113.5
    User todd
    IdentityFile ~/.ssh/pubkey-headless01-rsa
    LocalForward 58384 127.0.0.1:8384
" >> ~/.ssh/config
```

Assumption: that you already created and deployed an ssh key pair with a public key named `pubkey-headless01-rsa`. Read more here: <https://github.com/taw00/howto/blob/master/howto-ssh-keys.md>

Now, run it . . .

```bash
autossh -f -M 0 -N tunnel_headless_syncthing
```

If you can browse to <http://localhost:58384> without issue, then you can
slap that line into your `.bash_profile` so it runs at initial login . . .

```bash
echo "
# SSH Tunnel to …
# Syncthing administration service running at the headless01 server
# Reminder: tunnel_headless01_syncthing is defined in ~/.ssh/config
echo \"Launching SSH tunnel to Synthing admin on headless01 (203.0.113.5)\"
autossh -f -M 0 -N tunnel_headless01_syncthing
echo \"Now, browse to http://127.0.0.1:58384\"" >> ~/.bash_profile
```

---

## Browse and administer your Syncthing instance

You do this on your workstation. The SSH tunnel pipes that webUI from the remote
machine to your local machine.

- Browse to: <http://127.0.0.1:58384>
- Create a username and password within the application  
  - Navigate: `Actions` > `Settings` > `GUI`
  - Set `GUI Authentication User`: `syncthinguser` (can be anything)
  - Set `GUI Authentication Password`: `the syncthinguser is syncing w/ the syncthing service`
- I also like to set the default folder to something other than ~/Sync
  - Navigate: `Actions` > `Settings` > `General` > `Edit Folder Defaults`
  - Set `Folder Path`: `~/Syncthing` (you'll have to erase the `Sync` folder
    in the UI and the `/home/syncthinguser/Sync` folder on the filesystem)

Done! Now follow the docs for using the service.

---

## Good luck!

Comments and feedback to <t0dd@protonmail.com>
