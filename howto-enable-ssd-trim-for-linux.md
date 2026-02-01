# HowTo Improve SSD Write & Delete Performance for Linux Systems by Enabling ATA TRIM

***I.e. Enabling ATA TRIM discards for SSD (solid state drive) drive mounts***

Because of the way SSDs (Solid State Drives) work, saving new data can impact
performance. Namely, data marked as "deleted" have to be completely erased
before write. With traditional magnetic drives, data marked for deletion is
simply overwritten. Because SSDs have to take this extra step, performance can
be impacted and slowly worsens over time.

If, on the other hand, you can alert the operating system that it needs to wipe
deleted data in the background, writes (and deletes) can improve in performance.

## Caveats about breadth of support

Not all SSDs can support this as of this writing, nor do all variety of file
system formats, and you have to be using a newer linux kernel...

* Am I running at least Linux kernel 3.2?: `uname -a`
* Are my disks formatted as ext4?: `mount | grep ext4`    
  This shows (on my laptop) that `/` (root), `/boot`, and `/home` are formatted as ext4
* Can my SSD support this functionality?:`lsblk --discard`    
  This shows you two things, (1) what devices are at play and (2) do they, and their partitions support TRIM. If you see 0 values under DISC-GRAN and DISC-MAX, then don't continue, your SSD does not support TRIM.    
    
  On my laptop, for example, I see...
  - 512B for the first and 2G for the second values for all mount points listed above and swap
  - that they are all "luks" encrypted
  - and that there is only one SSD called device "sda". Since I know it is one device "sda" I should also see a filed called "discard_granularity" in "/sys/block/sda/queue/": `ls -l /sys/block/sda/queue/discard_granularity # Does this file exist?`    
    
  On my vultr.com instance, as a counter example, I see...
  - 0B and 0B respectively ... TRIM is not supported
* Some have noted that LUKS-encrypted mounts may weaken encryption if you enable TRIM. I honestly don't know what this really means or why, so do further research if this is a concern.

> _Special note: Though the swap partition may be listed for TRIM capable, do
> not set it to take extra action here. By virtue of the way swap works, this a
> non-issue._

Okay. Do you meet those criteria? Continue on..

----

#### Reference: Read more about this topic here...

* About TRIM: [Wikipedia: Trim (computing)](https://en.wikipedia.org/wiki/Trim_(computing))
* Generally: [Opensource.com: Solid state drives in Linux: Enabling TRIM for SSDs](https://opensource.com/article/17/1/solid-state-drives-linux-enabling-trim-ssds)
* Better detail that also addresses LUKS encrypted drives: [Blog: How to TRIM your encrypted SSD in Fedora 19](https://lukas.zapletalovi.com/2013/11/how-to-trim-your-ssd-in-fedora-19.html)

----

## Three methods of enablement

There are three routes you can take to enable TRIMing. (1) add "discard" to your mount settings, and/or (2) set up a cronjob
to perform periodic TRIM cleanup of deleted files, and/or (3) turn on systemd-managed periodic TRIM cleanup. Method 1 can
cause undo deletion performance loss (always wiping on every delete) so that is not recommended. Instead focus on method 2
or method 3 because they will clean up deleted data periodically as a background process.

### Method 1: "discard" in mount settings

Described here in order to be complete. This will tell the OS to wipe
upon delete instead of just marking the data. Downside: There is a performance
hit every time a deletion is performed.

Edit _fstab_ and add a "discard" parameter to the settings....

```
sudo nano /etc/fstab
```

Replace the line that looks like this (this is an example)...    
`UUID=2865a236-ab20-4bdf-b15b-ffdb5ae60a93 /                       ext4    defaults        1 1`    
...with one that looks like this...    
`UUID=2865a236-ab20-4bdf-b15b-ffdb5ae60a93 /                       ext4    defaults,discard        1 1`


### Method 2: Set up a cron job that periodically reaps data marked for deletion

For performance reasons, this is the recommended method UNLESS you have the TRIM systemd service available to you.

Do you have the systemd service available? `sudo systemctl status fstrim.timer` If your computer says "what the heck is
that?" then continue on. If that service is available, you should probably use that (see Method 3).

For my example, I am going to TRIM my `/` and `/home` partitions. My `/boot` partition is read-only 99.999% of the time so
write/delete performance is not a consideration.

Edit a new weekly cron job: `sudo nano /etc/cron.weekly/01-fstrim` as such and save...

```
#!/bin/sh
fstrim /
fstrim /home
```

Then make that job executable: `sudo chmod +x /etc/cron.weekly/01-fstrim`

> _Note: If you do a ton of writing and deleting on this system, feel free to move that `01-fstrim` file to `/etc/cron.daily/` or even `/etc/cron/hourly/`. When I run it manually, I see gigs of cleanup daily: `sudo fstrim -v /home`_

### Method 3: systemd-managed service that periodically reaps data marked for deletion

For performance reasons, this is the recommended method unless the service is simply unavailable to you. If it is not
available, choose "method 2" above. This method has another caveat: It trims only when your system is idle. If your system
is rarely idle, "method 2" is probably a better option. Doing both hurts nothing as well, but maybe some redundancy.

Do you have the systemd service available? `sudo systemctl status fstrim.timer` If your computer says "what the heck is
that?" then choose "method 2" described above.

This is simple to enable...
```
sudo systemctl enable fstrim.timer
sudo systemctl start fstrim.timer
```

----

## Extra step for LVM volumes

Your disk partitioning is likely managed by LVM. Edit lvm.conf and flip the bit that tells LVM to issue discards when it is
used to shrink or delete volumes: `sudo nano /etc/lvm/lvm.conf` and set `issue_discards = 1`

## Extra step for LUKS-encrypted partitions

Again, noted: There have been reports that enabling TRIM decreases encryption strength for LUKS-encrypted mountpoints. I
honestly don't know what this really means or why, so do further research if this is a concern.

Take a look at your block device again with `lsblk --discard`. Mine looks like this...

```
[taw@rh ~]$ lsblk --discard
NAME                                          DISC-ALN DISC-GRAN DISC-MAX DISC-ZERO
sda                                                  0      512B       2G         0
├─sda2                                               0      512B       2G         0
│ └─luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5        0      512B       2G         0
│   ├─fedora_rh-root                                 0      512B       2G         0
│   ├─fedora_rh-swap                                 0      512B       2G         0
│   └─fedora_rh-home                                 0      512B       2G         0
└─sda1                                               0      512B       2G         0
```

And let's take a look at that LUKS partition with `sudo cat /etc/crypttab`...

```
[taw@rh ~]$ sudo cat /etc/crypttab
luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5 UUID=a97ccef7-619b-4cee-8b2c-478f1f96e8e5 none
```

...and `sudo cryptsetup status luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5`...

```
[taw@rh ~]$ sudo cryptsetup status luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5
/dev/mapper/luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5 is active and is in use.
  type:    LUKS1
  cipher:  aes-xts-plain64
  keysize: 512 bits
  device:  /dev/sda2
  offset:  4096 sectors
  size:    999184384 sectors
  mode:    read/write
```

You will need to add a `discard` value to that "crypttab" configuration: `sudo nano /etc/crypttab` (edit and save)...

```
luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5 UUID=a97ccef7-619b-4cee-8b2c-478f1f96e8e5 none discard
```

And thus (after a reboot)...

```
[taw@rh ~]$ sudo cryptsetup status luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5
/dev/mapper/luks-a97ccef7-619b-4cee-8b2c-478f1f96e8e5 is active and is in use.
  type:    LUKS1
  cipher:  aes-xts-plain64
  keysize: 512 bits
  device:  /dev/sda2
  offset:  4096 sectors
  size:    999184384 sectors
  mode:    read/write
  flags:   discards
```

And if your root partition is LUKS-encrypted AND you set the partition to be TRIMed AND you want LVM trimming when shrinking
and deleting (see lvm.conf step above), the initial RAM disk needs to be regenerated using the following command:
`sudo dracut -f`

You need to reboot for these changes to take effect.

## All done! Good luck.

Comments and feedback  
—Todd Warner <a href="https://forms.gle/ogCeqcdqNSogYkPU8">(google contact form)</a>
