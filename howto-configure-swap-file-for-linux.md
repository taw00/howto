# HowTo Configure Swap with a Swap File for a Linux System

Your applications consume memory. What happens when an application maxes out
the memory pool available? It could destabilize your application and maybe your
system.

This situation is resolved by setting aside hard drive space to serve as a "swap
disk". This allows the operating system to artificially increase the RAM
available to that application. Remember though, that swap space is not a
replacement for RAM. If the system continually runs out of RAM, you don't have
enough RAM (or something else is wrong). Swap is "emergency memory".

# Swap disk? Swap file? Swap partition?

If you control your own build or installation process for a system, simply
ensure you have adequate swap configured as a partition during that process.
Almost all linuxes come with slick installation wizards now. And many/most
distributions create a swap partition for you. A partition is a dedicated chunk
of disk space that does nothing but swap operations. This is the most efficient
swap type (for disk-based swap anyway).

The purpose of this document, though, is to configure swap _after_ a system has
been provisioned or to configure swap after it was determined that the swap you
do have is not enough. For example, many VPS cloud instances do not deploy
instances that have swap already created. It's up to you to configure that or
create a swap file after the fact.

You can adjust your partitions after the fact using LVM, but it is much simpler
to use a swap file instead. What is a swap file? It's a file, on the file
system, that acts as a dedicated chunk of storage. In the past, swap files were
terribly inefficient, but now... they approach the performance of normal
dedicated disk-based swap partitions.

## Hey wait! Maybe I have swap already?

Open up a terminal and type this . . .

```shell
free
# and
swapon -s
```

This is what I see on one of my systems . . .

```plaintext
               total        used        free      shared  buff/cache   available
Mem:         3733528      675120      143652        1176     3208364     3058408
Swap:       12122104         256    12121848

Filename                               Type       Size     Used  Priority
/swapfile                              file       8388604  0     -2
/dev/zram0                             partition  3733500  256   100
```

Ah ha! I have swap already, and that lower-priority disk-based swap is more
than twice the size of my RAM. I should be good to go. But maybe it didn't
exist at all or was too small! If so, read on.

## Decision time. How much space to allocate?

First, you really should have RAM-based swap configured as primary. Disk-based
swap will be your fail-over swap: priority 100 for zram and -2 for disk.

What if I have no zram? You need to configure it. Here's a great article that
explains just that: <https://github.com/kurushimee/configure-zram>

I.e., how big of a swap file to I create?

Here's the general advice:

* Do you have far too little RAM? Buy more RAM (challenging if a laptop, I know)
* Do you have a relative small amount of RAM? A swap file sized 2x RAM should
  be sufficient.
* Do you have an overwhelming large amount of RAM? 1x RAM or even less is
  adequate. _Note: You need to really test this scenario - YMMV._
* Are you somewhere in the middle, or aren't sure? 2x RAM

I will show you how to implement a couple options...

## Creating a swap file and enabling it is easy:

<!-- NEW NEW WAY -->
```
# As root...
sudo su -

# Full path to your swap file.
swapfile=/swapfile

# Multiple (how many times the size of RAM?)...
m=2
```

### Prep the swap file - BTRFS version

There's a different process if the root file system is BTRFS or if it is EXT4. Check with `cat /etc/fstab`

If BTRFS, the process is MUCH slower and more convoluted. It is what it is …  
Read more about that here:  
<https://superuser.com/questions/1067150/how-to-create-swapfile-on-ssd-disk-with-btrfs>

```
# BTRFS version of swap file prep
# Create the file, soon to become a swap file
rm $swapfile
touch $swapfile

# To satisfy BTRFS's demand that it NOT be copy-on-write
lsattr $swapfile
# ... should look something like:
#     ---------------------- /swapfile
chattr +C $swapfile
lsattr $swapfile
# ... should now look something like:
#     ---------------C------ /swapfile

# Do some math and fill that file with nothing but zeros ...
bs=1024
size=$(free -b|grep Mem|awk '{print $2}')
size=$(($size*$m))
count=$(($size/$bs))
# ... now fill it (this *will* take some time and bog down your computer)
#     (that nice setting of 19 will *help* not thrash your machine, but this
#      is a heavy I/O process, so go take a nap or something)
nice -n 19 dd if=/dev/zero of=$swapfile bs=$bs count=$count
ls -lh $swapfile
```

### Prep the swap file - EXT4 version

Things are simpler and way faster with an ext4 file system.

```
# EXT4 version of swap file prep
# Size, in bytes
size=$(free -b|grep Mem|awk '{print $2}')
size=$(($size*$m))
size=$(printf "%.0f\n" $size)

# Create the swap file...
fallocate -l $size $swapfile
ls -lh $swapfile
```

### All file systems<br />Make it a swap file, turn it on, and add it to /etc/fstab

```
# All filesystem types
# Make it a swap file (has to have 0600 perms):
chmod 0600 $swapfile
mkswap $swapfile
ls -lh $swapfile

# Turn it on and check that it is running
swapon $swapfile
swapon --show
zramctl
free -h

# Enable even after reboot
cp -a /etc/fstab /etc/fstab.mybackup # backup your fstab file
echo "$swapfile none swap defaults 0 0" >> /etc/fstab

# check that it wrote and that it is correct
cat /etc/fstab
```

Finally, check that the swap priorities are correct. `/swapfile` priority
should be something like -1 or -2 and the zram priority should be something
like 100. You want the swap file to be a fallback (lower priority). The `swapon`
command will display the priority. If need be, you can force `/swapfile` to
have a negative priority by changing that `defaults` in the `fstab` file to
`defaults,p=-1` or similar. You should not have to do this though.

```shell
swapon -s
```


<!-- OLD NEW WAY```
# As root...
sudo su -

# Multiple (how many times the size of RAM?)...
m=2

# Size, in bytes
size=$(free -b|grep Mem|awk '{print $2}')
size=$(echo "$size * $m" | bc)
size=$(printf "%.0f\n" $size)

# Create the swap file...
fallocate -l $size /swapfile
chmod 0600 /swapfile
mkswap /swapfile

# Turn it on
swapon /swapfile

# You can see it running with a "swapon -s" or "free" command
free -h

# Enable even after reboot
cp -a /etc/fstab /etc/fstab.mybackup # backup your fstab file
echo '/swapfile none swap defaults 0 0' >> /etc/fstab
cat /etc/fstab # double check your fstab file looks fine
```-->
<!-- OLD WAY```
# As root...
sudo su -

# Size will be TOTAL_MEM * bs
#bs=256  # 1/4 times the size of RAM (1024/4 * 1)
#bs=512  # 1/2 times the size of RAM (1024/2 * 1)
#bs=1024 # One times the size of RAM (1024   * 1)
#bs=1536 # 1.5 times the size of RAM (1024   * 1.5)
bs=2048 # Twice the size of RAM (1024 * 2) - recommended if in doubt

# Create a swap file - it can take a bit to finish - be patient
TOTAL_MEM=$(free -k|grep Mem|awk '{print $2}')
dd if=/dev/zero of=/swapfile bs=$bs count=$TOTAL_MEM
chmod 0600 /swapfile

# Turn that file into a file formatted to be swap
mkswap /swapfile

# Turn it on
swapon /swapfile

# You can see it running with a "swapon -s" or "free" command
free -h

# Enable even after reboot
cp -a /etc/fstab /etc/fstab.mybackup # backup your fstab file
echo '/swapfile none swap defaults 0 0' >> /etc/fstab
cat /etc/fstab # double check your fstab file looks fine
```-->

## That's it! Good luck.  

Comments and feedback  
—Todd Warner <a href="https://forms.gle/ogCeqcdqNSogYkPU8">(google contact form)</a>

---

## Resources...

* A case made for "just enough" swap: <https://www.redhat.com/en/about/blog/do-we-really-need-swap-modern-systems>
* Really compelling advice given for specific ranges (login required): <https://access.redhat.com/solutions/15244>
