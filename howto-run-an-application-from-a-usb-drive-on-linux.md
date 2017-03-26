# HowTo Run Applications from a USB Drive on Linux

Because of the nature of USB drives, you can't, by default, run an application
_from_ the USB drive. USB drives are typically formatted as FAT32 filesystems
(legacy microsoft cruft) and FAT32 doesn't really understand "permissions" per
ce. And since most USB drives are used for "data" and not "application"
permissions are usually fixed at 644 for files and 755 for directories. And
they can't be changed with `chmod` like a normal linux file system.

## Assumptions

On a Ubuntu system, I believe USB drives automount at
`/media/<username>/<some-drive-label>`

On a Fedora or Red Hat system, it will be mounted at
`/run/media/<username>/<some-drive-label>`

For this exercise, we'll just assume Fedora's rules (more standard anyway) and
you can adjust if you are using something else.

## So, what to do?

This is where the fuse filesystem once again proves itself to be the
swiss-army-knife of filesystems. Someone made it is possible to mirror a
directory, into a fuse-mount, and allow you to change the permissions of the
files within that mirror. Pretty brilliant actually.

What you are going to do is mount your USB drive normally and then "bind-mount"
it to another directory, setting different permissions in the process.

## First, install `bindfs`

```
# On Fedora
sudo dnf install -y bindfs
```

```
# On CentOS 7 or Red Hat Enterprise Linux 7
sudo yum install -y bindfs
```

```
# On Ubuntu
sudo apt install bindfs
```

## Insert USB stick and note the mountpoint

For this example, the username will be `todd`

Once inserted...

```
ll /run/media/todd
# ..or it could be...
ll /media/todd
```

You should see your USB drive there. Let's look at it...

```
ll /run/media/todd/toddsusb
```

It'll look something like this...

```
drwxr-xr-x. 9 todd todd     4096 Mar 15 08:43 backup
-rw-r--r--. 1 todd todd   445944 Mar 22 20:30 myapplication
-rw-r--r--. 1 todd todd 12197864 Mar 22 20:30 some-data.dat
```

That `myapplication` can't be run from the USB. And you can't `chmod +x
myapplication` either.

## Use `bindfs` to mirror and re-permission

*Create a directory to bind-mount to...*

```
cd -
mkdir myusb
```

*Mount the mirror*

```
cd -
sudo bindfs -M todd -p0700,u+X /run/media/todd/toddsusb myusb
ll myusb
```

*You should see, in `myusb`...*

```
drwx--x---. 9 todd todd     4096 Mar 15 08:43 backup
-rwx------. 1 todd todd   445944 Mar 22 20:30 myapplication
-rwx------. 1 todd todd 12197864 Mar 22 20:30 some-data.dat
```

*`myapplication` is now executable. Run it with...*

```
myusb/myapplication
```

Remember. This is a mirror. Whatever happens in this directory will be
reflected in the originating directory. The permissions will remain unchanged.


## Un-mounting

You can't just "un-mount" or "eject" the USB drive. You have to un-mount the
mirror first, then un-mount the originating directory.

```
cd -
sudo umount myusb
```

Now safely un-mount the original. Either with a filesystem-menu or from the commandline...

```
sudo umount /run/media/todd/toddsusb
```


## That's it! Pretty powerful, actually. I hope this was helpful.

Feedback and comments welcome at <t0dd@protonmail.com>

