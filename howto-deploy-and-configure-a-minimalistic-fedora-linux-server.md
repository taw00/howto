# HowTo: Deploy and Configure a Fedora Linux Operating System

***...to serve as a minimalist server platform***

Note: These are instruction for deploying a base- or minimal- system. No
application related configurations are made here.

**Summary -- the objectives are straight-forward:**

<!-- TOC min:2 max:2 link:true update:true -->

- [HowTo: Deploy and Configure a Fedora Linux Operating System](#howto-deploy-and-configure-a-fedora-linux-operating-system)
  - [[0] Deploy a minimal operating system](#0-deploy-a-minimal-operating-system)
    - [Example: A cloud service installation, for example Vultr](#example-a-cloud-service-installation-for-example-vultr)
    - [Example: A traditional bare-metal server installation](#example-a-traditional-bare-metal-server-installation)
  - [[1] Fully update the system](#1-fully-update-the-system)
  - [[2] Add swap space to give your system memory some elbow room...](#2-add-swap-space-to-give-your-system-memory-some-elbow-room)
  - [[3] Create user, setup SSH and sudo access...](#3-create-user-setup-ssh-and-sudo-access)
  - [[4] Install and Configure FirewallD](#4-install-and-configure-firewalld)
  - [[5] Install and Configure Fail2Ban](#5-install-and-configure-fail2ban)
  - [[6] Minimize root user exposure](#6-minimize-root-user-exposure)
  - [[7] Reboot and test logins](#7-reboot-and-test-logins)
  - [ALL DONE!](#all-done)
  - [Appendix - Advanced Topics](#appendix---advanced-topics)
    - [Improve SSD Write & Delete Performance for Linux Systems by Enabling ATA TRIM](#improve-ssd-write--delete-performance-for-linux-systems-by-enabling-ata-trim)

<!-- /TOC -->

> A note about minimum requirements. The application you deploy to the system
> dictates the beefy-ness of your system. For our purposes we are going to use
> a system with 2G RAM and double that for swapspace as our example.

## [0] Deploy a minimal operating system

There are two primary means to install the operating system that will covered
here. (1) Via a cloud service, like Vultr.com, or (2) via a traditional
bare-metal blade, server, white-box, whatever.

### Example: A cloud service installation, for example Vultr

**Deploy to Vultr**
  - Browse to [https://my.vultr.com/](https://www.vultr.com/?ref=7047925)
  - Create an account and login.
  - Click the ( + ) button.
  - Step (1): Choose some location
  - Step (2): Choose 64 bit OS and Fedora
  - Step (3): Choose 4096MB(4GB) RAM, 2CPU 60GB SSD
  - Step (6): Set up SSH keys...
    - This will make your life more pleasant and secure.
      [Read more here](https://github.com/taw00/howto/blob/master/howto-ssh-keys.md)
      for this process. Vultr also has a [great howto](https://github.com/taw00/howto/blob/master/howto-ssh-keys.md).
    - Add (upload) the newly created SSH _public_ key to setup process.
  - Step (7): Pick a hostname and label, "system00" or whatever.
  - Deploy!

**Post initial deployment to Vultr**

  - **Test and troubleshoot your root SSH settings** &mdash; ssh into your Vultr
    instance: `ssh root@<IP ADDRESS OF YOUR INSTANCE>` If you set up ssh keys
    right, it should just log you right in. If not, log in using your root
    password and troubleshoot why your ssh key setup is not working right and get it working (see above) so that you don't need a password to ssh into your system.
  - **Change your root password** &mdash; `passwd` &mdash; to something longer
    and ideally random. I use [Lastpass](https://www.lastpass.com/) to generate
    passwords.
   - **[optional] Change your timezone settings** &mdash; The default is set to
    UTC. If you prefer times listed in your local timezone, change it. FYI:
    Some time-date stamps are always listed in UTC, like many log files.

```
# As root user
# Find and cut-n-paste your timezone...
timedatectl list-timezones # arrow keys to navigate, "q" to quit
# Change it (example, eastern time, USA)...
timedatectl set-timezone 'America/New_York'
# Don't like that? Change it back...
timedatectl set-timezone 'UTC'
# Test it...
date
```


### Example: A traditional bare-metal server installation

I leave it as an exercise for the reader to perform a bare-metal installation
of  Fedora, CentOS, or even RHEL. For Fedora, go here - https://getfedora.org/
For CentOS, go here - https://www.centos.org/download/ For Fedora, I recommend
the "Server" install. You need only a minimum configuration. Dependency
resolution of installed RPM packages per these instructions will bring in
anything you need.

As you walk through the installation process, choose to enable swap, it needs
to be at least equal to the size of RAM, 2GB and ideally twice that, 4GB. Like
I said earlier though, swap size is a much larger discussion than what we can
do here. 2x RAM is a good starting point.

Once installed, follow similar process as the Vultr VPS example above for SSH
configuration. I.e., General instructions for the creation and initial
configuration of SSH can be found
[here](https://github.com/taw00/howto/blob/master/howto-ssh-keys.md).


## [1] Fully update the system

Install a few vitals and then update everything  
As `root`...

```
# If Fedora...
dnf install -y vim-enhanced findutils screen
dnf upgrade -y

# If CentOS7 or RHEL7...
#yum install -y epel-release
#yum install -y vim-enhanced findutils screen
#yum update -y
```

## [2] Add swap space to give your system memory some elbow room...

Vulr initially boots with no configured swap. A bare-metal install will probably include swap. You can determine if you have swap configured with...

```
swapon -s
```

A reasonable rule of thumb is to configure swap to be twice the size of your RAM.
Swap-size is more art than science, but your system will be brutalized occassionally...
2-times your RAM is a good choice. These instructions and more can be found at:   <https://github.com/taw00/howto/blob/master/howto-configure-swap-file-for-linux.md>

```
# As root...

# Multiple (how many times the size of RAM?)...
m=2

# Size, in bytes...
size=$(free -b|grep Mem|awk '{print $2}')
size=$(echo "$size * $m" | bc)
size=$(printf "%.0f\n" $size)

# Create a swapfile...
fallocate -l $size /swapfile
chmod 0600 /swapfile
mkswap /swapfile

# Turn it on
swapon /swapfile

# You can see it running with a "swapon -s" or "free" command
free -h

# Enable even after reboot
cp -a /etc/fstab /etc/fstab.mybackup # backup your fstab file
echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
cat /etc/fstab # double check that your fstab file looks fine
```


## [3] Create user, setup SSH and sudo access...

During the installation process using the wizard you *may* be asked to create a
user (vultr.com does not do this). Do it. Additionally, choose to give this
user administration rights (they will be able to `sudo`).

While you may be able to do that during the set up process, included here is the
post-installation instruction for doing the same thing. The username in this
example is `todd` (hey! that's me!)...

```
# Log into the system as root user.
# If the user does not exist, do this...
useradd -G wheel todd
passwd todd

# If the user already exists, do this...
# Fedora/CentOS/RHEL example
usermod -a -G wheel todd
# Ubuntu example, for comparison
#usermod -a -G sudoers todd
```

**IMPORTANT:** Work through the SSH instructions (see the Vultr example above) and set
it up so you can ssh into the system as your normal user without a password from your
desktop system. Read more about setting up SSH keys here:  
<https://github.com/taw00/howto/blob/master/howto-ssh-keys.md>


> ***Recommendation1:***
> Choose a difficult scrambled password for both `root` and your `todd` user.
> Then ensure ssh keys are set up so you can ssh to the instance without having
> to type passwords.

> ***Recommendation2:***
> Edit the `/etc/sudoers` configuration file and uncomment the `%wheel` line
> that includes the `NOPASSWD` qualifier. This will allow you to `sudo` as the
> `todd` user without having to cut-n-paste a password all the time.


## [4] Install and Configure FirewallD

See also: <https://github.com/taw00/howto/blob/master/howto-configure-firewalld.md>

As root...

**Install**

```
# If Fedora...
dnf install -y firewalld

# If CentOS7 or RHEL7...
#yum install -y firewalld
```


**Configure**

> _Note: Firewall rules can be a complicated topic. These are bare bones
> git-er-done instructions. You may want to investigate further refinement. It
> will get you started though._


```
# Is firewalld running?
# Turn on and enable firewalld if not already done...
firewall-cmd --state
systemctl start firewalld.service
systemctl enable firewalld.service

# Determine what the default zone is.
# On vultr, for example, the default zone is FedoraServer (it is the assumption
# for this example)
firewall-cmd --get-active-zone
# ...or better yet...
firewall-cmd --list-all |grep -iE '(active|interfaces|services)'

# Whatever that default zone is, that is the starting conditions for your
# configuration. For this example, I am going to demonstrate how to edit my
# default configuration on my Fedora Linux system: FedoraServer. You _could_
# create your own zone definition, but for now, we will be editing the
# configuration that is in place.

# FedoraServer usually starts with ssh, dhcp6-client, and cockpit opened up I
# want to allow SSH, but I don't want cockpit running all the time and by
# having a static IP, dhcpv6 service is unneccessary.
firewall-cmd --permanent --add-service ssh
firewall-cmd --permanent --remove-service dhcpv6-client
firewall-cmd --permanent --remove-service cockpit

# Rate limit incoming ssh and cockpit (if configured on) traffic to 10/minute
firewall-cmd --permanent --add-rich-rule='rule service name=ssh limit value=10/m accept'
#firewall-cmd --permanent --add-rich-rule='rule service name=cockpit limit value=10/m accept'

# did it take?
firewall-cmd --reload
firewall-cmd --state
firewall-cmd --list-all
```

_After you `--list-all`, if you see a service you do not wish to be available,
feel free to remove it following the pattern we demonstrated above._


**Some references:**

* FirewallD documentation: <https://fedoraproject.org/wiki/Firewalld>
* Rate limiting as we do above: <https://www.rootusers.com/how-to-use-firewalld-rich-rules-and-zones-for-filtering-and-nat/>
* More on rate limiting: <https://serverfault.com/questions/683671/is-there-a-way-to-rate-limit-connection-attempts-with-firewalld>
* And more: <https://itnotesandscribblings.blogspot.com/2014/08/firewalld-adding-services-and-direct.html>
* Interesting discussion on fighting DOS attacks on http: <https://www.certdepot.net/rhel7-mitigate-http-attacks/>
* Do some web searching for more about firewalld


## [5] Install and Configure Fail2Ban

See also: <https://github.com/taw00/howto/blob/master/howto-configure-fail2ban.md>

**Install `fail2ban`...**

As root...

```
# If Fedora...
dnf install -y fail2ban fail2ban-systemd

# If CentOS or RHEL
#yum install epel-release # if not already installed
#yum install -y fail2ban fail2ban-systemd

# If Debian or Ubuntu
#apt install -y fail2ban
```

If you are not using FirewallD, and instead are using IPTables for your
firewall, uninstall fail2ban-firewalld (for the Red Hat-based systems only).

```
# If Fedora...
dnf remove -y fail2ban-firewalld

# If CentOS or RHEL
#yum remove -y fail2ban-firewalld
```

**Configure `fail2ban`...**

Edit `/etc/fail2ban/jail.d/local.conf` _(Optionally `/etc/fail2ban/jail.local`
instead)_


Copy this; paste; then save...

```
[DEFAULT]
# Ban hosts for one hour:
bantime = 3600

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

For more about setting up "send-only email", read
[this](https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md).


**Enable `fail2ban` and restart...**

```
systemctl enable fail2ban
systemctl restart fail2ban
```

**Monitor / Analyze**

Watch the IP addresses slowly pile up by occasionally looking in the SSH jail...

```
fail2ban-client status sshd
```

Also watch...

```
journalctl -u fail2ban.service -f
```
```
tail -F /var/log/fail2ban.log
```

**Reference:**

* <https://fedoraproject.org/wiki/Fail2ban_with_FirewallD>
* <https://en.wikipedia.org/wiki/Fail2ban>
* <http://www.fail2ban.org/>


## [6] Minimize root user exposure

***Turn off SSH logins for root...***

Attackers _love_ to attempt to login to root via SSH. Turn that off.

* Edit `/etc/ssh/sshd_config`
* Either add or edit these lines (add only if the setting does not already
  exist)...

```
PermitRootLogin no
AllowUsers todd
PasswordAuthentication no
# Probably already set to no...
ChallengeResponseAuthentication no
```

_Note: `AllowUsers` can be set to multiple users._

* Once complete, double check your work...
* **IMPORTANT:** In another terminal ssh in as your normal user ("todd" in our example).
  If you screw up SSH configuration, that user will still be logged in and can fix
  things. Otherwise, you are in danger of being locked out.
* Triple check your work and restart sshd: `systemctl restart sshd

**Test your configuration...**`
* After restarting sshd, ssh-login with that "todd" user in another terminal. If you
  configured things correctly, it will work.
* In yet another terminal, attempt to login with ssh as "root". Your new configuration
  should disallow this. If so, this is correct behavior.
* All tested and better now? Good. Your system is now significantly more secure.

## [7] Reboot and test logins

In one of your terminals where you logged in as your normal user ("todd" in our
example)...

```
sudo reboot
```

Once rebooted...
* Attempt to login with `ssh` as your normal user. This shoudl work.
* Attempt to login with `ssh` as root. This should not work.


&nbsp;

---

## ALL DONE!

If all went well, you have an efficient, working, and secure system prepared to
run most general-purpose applications. I hope this was helpful.

Got a dash of feedback? Send it my way <https://keybase.io/toddwarner>    

&nbsp;

&nbsp;

---

## Appendix - Advanced Topics

### Improve SSD Write & Delete Performance for Linux Systems by Enabling ATA TRIM

Because of the way SSDs (Solid State Drives) work, saving new data can impact performance. Namely, data marked as "deleted" have to be completely erased before write. With traditional magnetic drives, data marked for deletion is simply overwritten. Because SSDs have to take this extra step, performance can be impacted and slowly worsens over time.

If, on the other hand, you can alert the operating system that it needs to wipe deleted data in the background, writes (and deletes) can improve in performance.

To learn more, follow this link: <https://github.com/taw00/howto/blob/master/howto-enable-ssd-trim-for-linux.md>
