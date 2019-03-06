# HowTo: Deploy and Configure a Fedora Linux Operating System
***...to serve as a minimalist server platform***

Note: These are instruction for deploying a base- or minimal- system. No
application related configurations are made here.

## Summary -- the objectives are straight-forward:

<!-- TOC min:2 max:2 link:true update:true -->

- [HowTo: Deploy and Configure a Fedora Linux Operating System](#howto-deploy-and-configure-a-fedora-linux-operating-system)
  - [Summary -- the objectives are straight-forward:](#summary----the-objectives-are-straight-forward)
  - [[1] Deploy a minimal operating system](#1-deploy-a-minimal-operating-system)
    - [Example: A cloud service installation, for example Vultr](#example-a-cloud-service-installation-for-example-vultr)
    - [Example: A traditional bare-metal server installation](#example-a-traditional-bare-metal-server-installation)
  - [[2] Fully update the system and reboot](#2-fully-update-the-system-and-reboot)
  - [[3] Create user, setup SSH and sudo access...](#3-create-user-setup-ssh-and-sudo-access)
  - [[4] Minimize root user exposure](#4-minimize-root-user-exposure)
  - [[5] Install and Configure FirewallD](#5-install-and-configure-firewalld)
  - [[6] Install and Configure Fail2Ban](#6-install-and-configure-fail2ban)
    - [Install `fail2ban`...](#install-fail2ban)
    - [Configure `fail2ban`...](#configure-fail2ban)
    - [Enable `fail2ban` and restart...](#enable-fail2ban-and-restart)
    - [Monitor / Analyze](#monitor--analyze)
    - [Reference:](#reference)
  - [ALL DONE!](#all-done)
  - [Appendix - Advanced Topics](#appendix---advanced-topics)
    - [Improve SSD Write & Delete Performance for Linux Systems by Enabling ATA TRIM](#improve-ssd-write--delete-performance-for-linux-systems-by-enabling-ata-trim)

<!-- /TOC -->

> A note about minimum requirements. The application you deploy to the system
> dictates the beefy-ness of your system. For our purposes we are going to use
> a system with 2G RAM and double that for swapspace as our example.

## [1] Deploy a minimal operating system

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

  - **Add swap space** to give your system memory some elbow room...

Vulr initially boots with no configured swap. A reasonable
[rule of thumb](https://github.com/taw00/howto/blob/master/howto-configure-swap-file-on-linux.md)
is to configure swap to be twice the size of your RAM. Swap-size is more art
than science, but your system will be brutalized occassionally... 2-times your
RAM is a good choice.

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
cat /etc/fstab # double check your fstab file looks fine
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


## [2] Fully update the system and reboot

As `root`...

```
# If Fedora...
dnf upgrade -y
reboot

# If CentOS7 or RHEL7...
#yum install -y epel-release
#yum update -y
#reboot
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

**IMPORTANT:** Work through the SSH instructions (see Vultr example) and set it
up so you can ssh into the system as your normal user without a password from
your desktop system.


> ***Recommendation1:***
> Choose a difficult scrambled password for both `root` and your `todd` user.
> Then ensure ssh keys are set up so you can ssh to the instance without having
> to type passwords.

> ***Recommendation2:***
> Edit the `/etc/sudoers` configuration file and uncomment the `%wheel` line
> that includes the `NOPASSWD` qualifier. This will allow you to `sudo` as the
> `todd` user without having to cut-n-paste a password all the time.



## [4] Minimize root user exposure

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

* Once complete, restart sshd: `sudo systemctl restart sshd`
* IMPORTANT TEST: While remaining logged into "todd" in one terminal, test that
  you can still ssh-in to the machine using another terminal. If not, you need
  to troubleshoot. If you lose that connection or are logged out from the other
  terminal, you may have lost access to the machine. Fair warning.
* All tested and better now? Good. Your system is now significantly more secure.


## [5] Install and Configure FirewallD

As a normal user (example `todd`)...

**Install**

```
# If Fedora...
sudo dnf install -y firewalld

# If CentOS7 or RHEL7...
#sudo yum install -y firewalld
```


**Configure**

> _Note: Firewall rules can be a complicated topic. These are bare bones
> git-er-done instructions. You may want to investigate further refinement. It
> will get you started though._


```
# Is firewalld running?
# Turn on and enable firewalld if not already done...
sudo firewall-cmd --state
sudo systemctl start firewalld.service
sudo systemctl enable firewalld.service

# Determine what the default zone is.
# On vultr, for example, the default zone is FedoraServer (it is the assumption
# for this example)
sudo firewall-cmd --get-active-zone
# ...or better yet...
sudo firewall-cmd --list-all |grep -iE '(active|interfaces|services)'

# Whatever that default zone is, that is the starting conditions for your
# configuration. For this example, I am going to demonstrate how to edit my
# default configuration on my Fedora Linux system: FedoraServer. You _could_
# create your own zone definition, but for now, we will be editing the
# configuration that is in place.

# FedoraServer usually starts with ssh, dhcp6-client, and cockpit opened up I
# want to allow SSH, but I don't want cockpit running all the time and by
# having a static IP, dhcpv6 service is unneccessary.
sudo firewall-cmd --permanent --add-service ssh
sudo firewall-cmd --permanent --remove-service dhcpv6-client
sudo firewall-cmd --permanent --remove-service cockpit

# Rate limit incoming ssh and cockpit (if configured on) traffic to 10/minute
sudo firewall-cmd --permanent --add-rich-rule='rule service name=ssh limit value=10/m accept'
#sudo firewall-cmd --permanent --add-rich-rule='rule service name=cockpit limit value=10/m accept'

# did it take?
sudo firewall-cmd --reload
sudo firewall-cmd --state
sudo firewall-cmd --list-all
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


## [6] Install and Configure Fail2Ban

### Install `fail2ban`...

```
# If Fedora...
sudo dnf install -y fail2ban fail2ban-systemd

# If CentOS or RHEL
#sudo yum install epel-release # if not already installed
#sudo yum install -y fail2ban fail2ban-systemd

# If Debian or Ubuntu
#sudo apt install -y fail2ban
```

If you are not using FirewallD, and instead are using IPTables for your
firewall, uninstall fail2ban-firewalld (for the Red Hat-based systems only).

```
# If Fedora...
sudo dnf remove -y fail2ban-firewalld

# If CentOS or RHEL
#sudo yum remove -y fail2ban-firewalld
```

### Configure `fail2ban`...

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


### Enable `fail2ban` and restart...

```
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
```

### Monitor / Analyze

Watch the IP addresses slowly pile up by occasionally looking in the SSH jail...

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

### Reference:

* <https://fedoraproject.org/wiki/Fail2ban_with_FirewallD>
* <https://en.wikipedia.org/wiki/Fail2ban>
* <http://www.fail2ban.org/>



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
