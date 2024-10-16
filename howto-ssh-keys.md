# HowTo Create and Use SSH Keys on Linux

SSH is short for "secure shell". SSH is used to "log in" to a remote system
through a secure communication channel. So, for example, if you have a remote
system, "x.y.z", and you are user, "todd" on that system, you can log into (ssh
into) that machine with a simple command: `ssh todd@x.y.z`.

Each time you log into that remote system, you need to enter a password. This
is fine if you only occassionally log in, but a better way. A more secure way
really, is to use a generated SSH key pair.

With these instructions, you will generate an public key and a private key.
You will store the private key locally and copy the public key to the remote
system. This establishes a fixed authenticated association between one user on
the local machine and one user on the remote machine. Once established, you
will no longer be required to enter a password when ssh'ing in.


<!-- TOC START min:2 max:2 link:true update:true -->
- [Create a SSH public private key pair](#create-a-ssh-public-private-key-pair)
- [Using the SSH key pair](#using-the-ssh-key-pair)
- [Lock down the root user...](#lock-down-the-root-user)

<!-- TOC END -->


## Create a SSH public private key pair

Let's say the username on the remote system is username **todd**...

Log into your local machine and create a 2048-bit or 4096-bit rsa key-pair...

```
ssh-keygen -t rsa -b 4096 -C "This is a test key"
```

By default, this will create two keys in `/home/USERNAME/.ssh/`: `id_rsa` and
`id_rsa.pub`. Of course, the one that ends in `.pub` is the public key and the
one without is the private key.

You can keep the default, but I usually change the name of the key-pair to
indicate a particular purpose. For this example, I am creating this key-pair
to be used to log into machine x.y.z, so I am going to name them `xyzkey` and
`xyzkey.pub`. You can use the same key-pair for any number of machines, maybe
you differientiate by type of machine, and so you would name them similarly,
like `prod-webservers` and `prod-webservers.pub`.

_The password._

Upon creation, you can create it with a password. Often, administrators will
create the keys without a password. You already log into your local account
very securely, and you are creating an encrypted pipe to the remote system
using this key pair. It is very common and not considered bad practice to
generate a key pair with no-password, or a much simpler password than the login
passwords for the remote system. Some admins intentionally change and forget
the login passwords for remote systems and leverage their SSH key-pair only.
Something to think about. Experiment on your own.


## Using the SSH key pair

Let's assume you created a passwordless key-pair named `xyzkey` and `xyzkey.pub`.
How do you use it?

* Backup the set - a USB stick, keybase fs, lastpass, ...somewhere secure

* ssh into your remote system (hopefully the last time you need to use your
  username and password): `ssh todd@x.y.z`

* Create the .ssh directory and set up permissions...

```
mkdir ~/.ssh
touch ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/*
```

Note: If the permissions aren't correct, SSH logins will fail.


* Edit the `~/.ssh/authorized_keys` file and cut and past the
  contents of your `.pub` key (it's one long line of txt) into that file. The
  contents look something like this, and there can be multiple keys (one per line):<br />
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDfTc7Zc72HvjoirIAiYXaeoTW8TxIKnQghmffmlwe6Z1xU88JNRPk03ZTfrx/MaHNE8mXW+OakCOBbpXOEOLJG+iscD9G/CRP9ki3u4l5Ttujf9Qp/ZFc9Fx4C85LRa6dc8GfPN0Imv9mL9nT1QlrYgAmi2QukYKHe64E9e9H7BCZPqs0rvqkiiA2cPAl3psDCZZ9GENGB9OVw6T7swwjWemJjzMPpBEeeUJ6g6fp0iZW6AJw0LVzOLuIdhskLchj9XMAD1O1lxsLDz4BTyH9czF4RFjFoePgdaaodagVjAc2Co86H81b3do1GzUWCQogurM9y/zdlsbQ1v66DLONHJAlYdTdg29lRvfBH8ZB0aY7i4Go1PnvJkMSuDg8kT0YUDoVUUXveq8xXQk29J5JdEl2mS13AfqIyghBLiT1weUIuSLjMQkufREYRayygYBMST59fpB4/gAKohAGiyGucRwTNZ5/kyHWed7yEMe+/Qkl80Pl5Rs55N2ZcGrN8j6HcGx4zOWp/6BqEmEV2w6BY9AFYUPYOWgdjVmhFwHuypKQdJ15sOHBzFfJZWsbc7j5eSywVRyarKD9quWL4m2LR01Bdv9A9FMRtCAa3XrjWRPS8BSuL9QOwiiUsO6V6v+QX1IDXK314mCEk3DaBeuQxQQiqjMGlE8b2K1Uei6dmXw== This is a test key
```

Another way to do this is to append the key to the remote system's configuration from the local machine...

```
cat ~/.ssh/xyzkey.pub | ssh todd@x.y.z 'cat - >> ~/.ssh/authorized_keys'
```


* Log out of the remote machine and test your SSH key...

```
ssh -i ~/.ssh/xyzkey todd@x.y.z
```

* More permanently, you really need to add a config file to .ssh (on the local machine)...

```
cd ~/.ssh
touch config
chmod 600 config
```

Edit that file -- `config` -- and add a stanza that looks like this...

```
# My remote test box gets an alias and configuration
host xyz
    #hostname IP_or_HOSTNAME_OF_REMOTE_SYSTEM, for example...
    hostname x.y.z
    user todd
    IdentityFile ~/.ssh/xyzkey
    # Optional settings - `man ssh_config` to learn more
    #ForwardX11Trusted yes
    #ForwardAgent yes
    #ForwardX11 yes
    #GatewayPorts yes
    #IdentitiesOnly yes
```

* Now things become even easier. Here's some examples...

```
# This will log in as todd@x.y.z
ssh xyz

# This will log in as root@x.y.z
# Note: You will have to configure root's authorized_keys as well for this.
ssh root@xyz

# This will copy a file testfile.txt to x.y.z
scp testfile.txt xyz:

# Executing a command...
ssh xyz mkdir directory1

# rsyncing stuff
rsync --progress -r Documents todd@xyz:directory1
```


## Lock down the root user...

You can now ssh using a password, or using the ssh-key pair.

Let's lock down root from remote access. Before we can do that, you will want
to set up the normal user with sudo access, and then turn off access to root
from remote ssh.

### `sudo` setup for a normal user...

In our example, the normal user username is "todd".

**Add "todd" to the "wheel" user group**

```
usermod -a -G wheel todd
```

**(optional, but recommended)** Turn off password checking upon sudo...

* Edit the `/etc/sudoers` configuration file
* uncomment the `%wheel` line that includes the `NOPASSWD` qualifier
* You can now execute any sudo command without having to enter the admin
  password.
* Test it: `sudo ls -l /root/`

### Turn off "root" user remote ssh logins...

In our example, the normal user username is "todd".

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
