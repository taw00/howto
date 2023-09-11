# HowTo Configure Swap with a Swap File for a Linux System

Your applications consume memory. What happens when an application maxes out
the memory pool available? It could destabilize your application and maybe your
system.

This situation is resolved by setting aside harddrive space to serve as a "swap
disk". This allows the operating system to artificially increase the RAM
avialable to that application. Remember though, that swap space is not a
replacement for RAM. If the system continually runs out of RAM, you don't have
enough RAM (or something else is wrong). Swap is "emergency memory".

# Swap disk? Swap file? Swap partition?

If you control your own build or installation process for a system, simply
ensure you have adequate swap configured as a partition during that process.
Almost all linuxes come with slick installation wizards now. And many/most
distributions create a swap partition for you. A partition is a dedicated chunk
of disk space that does nothing but swap operations. This is the most efficient
swap type. 

The purpose of this document, though, is to configure swap _after_ a system has
been provisioned or to configure swap after it was determined that the swap you
do have is not enough. For example, many VPS cloud instances do not deploy
instances that have swap already created. It's up to you to configure that or
create a swap file after the fact.

You can adjust your partitions after the fact using LVM, but it is much simpler
to use a swap file instead. What is a swap file? It's a file, on the file
system, that acts as a dedicated chunk of storage. In the past, swap files were
terribly inefficient, but now... they approach the performance of normal
dedicated swap partitions.

## Hey wait! Maybe I have swap already?

Open up a terminal and type this...

```
free -h
```

This is what I see on one of my systems...

```
              total        used        free      shared  buff/cache   available
Mem:           2.0G        485M        113M        276K        1.4G        1.3G
Swap:          3.9G         11M        3.9G
```

Ah ha! I have swap already, and twice the size of my RAM. I should be good to
go. But maybe it didn't exist at all or was too small! If so, read on.

## Decision time. How much space to allocate?

I.e., how big of a swap file to I create?

Here's the general advice:

* Do you have far too little RAM? Buy more RAM
* Do you have a relative small amount of RAM? A swap file sized 2x RAM should
  be sufficient.
* Do you have an overwelming large amount of RAM? 1x RAM or even less is
  adequate. _Note: You need to really test this scenario - YMMV._
* Are you somewhere in the middle, or aren't sure? 2x RAM

I will show you how to implement a couple options...

## Creating a swap file and enabling it is easy:

<!-- NEW WAY -->
```
# As root...
sudo su -

# Multiple (how many times the size of RAM?)...
m=2

# Size, in bytes
size=$(free -b|grep Mem|awk '{print $2}')
size=$(echo "$size * $m" | bc)
size=$(printf "%.0f\n" $size)

# Create the swapfile...
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

<!-- OLD WAY```
# As root...
sudo su -

# Size will be TOTAL_MEM * bs
#bs=256  # 1/4 times the size of RAM (1024/4 * 1)
#bs=512  # 1/2 times the size of RAM (1024/2 * 1)
#bs=1024 # One times the size of RAM (1024   * 1)
#bs=1536 # 1.5 times the size of RAM (1024   * 1.5)
bs=2048 # Twice the size of RAM (1024 * 2) - recommended if in doubt

# Create a swapfile - it can take a bit to finish - be patient
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
echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
cat /etc/fstab # double check your fstab file looks fine
```-->

## That's it! Good luck.  

Please send comments and feedback to <t0dd@protonmail.com>

---

## Resources...

* A case made for "just enough" swap: <https://www.redhat.com/en/about/blog/do-we-really-need-swap-modern-systems>
* Really compelling advice given for specific ranges (login required): <https://access.redhat.com/solutions/15244>
