# Miscellaneous Useful Things!

Here's my grab-bag of random useful things that don't yet warrant their own
howtos.


## HowTo: What's my external IP address?

Such a simple thing, but not always obvious. You effectively have to look from
the outside in.

### opendns.com

```
dig +short myip.opendns.com @resolver1.opendns.com
```

### icanhazip.com

An acquaintence of mine (Major Hayden) runs this simple website that so many
people use.

```
curl https://icanhazip.com/
```

### SSH into a box and "look back at yourself"

```
ssh <some user>:<some machine>
```

```
# On most systems you can use $SSH_CLIENT as well
echo $SSH_CONNECTION | cut -d' ' -f1
```


---


## HowTo: Port Introspection

If you have exposed ports, your system is, well, exposed. I am going to dump
diagnotist tidbits here over time. By the way, if you do have ports exposed,
make sure you take some steps to secure them. Here's a start: <>

Let me start with a particularly useful one liner.

### Watch port 22 and show "ESTABLISHED" connections who aren't localhost

```
sudo watch -n10 "netstat -ntu | grep :22| grep ESTAB | awk '{print \$5}' | cut -d: -f1 | grep -v 127.0.0.1 | sort"
```

And if this is a remote server. Let's exclude our own IP address...

```
sudo watch -n10 "netstat -ntu | grep :22| grep ESTAB | awk '{print \$5}' | cut -d: -f1 | grep -v 127.0.0.1 | grep -v `echo $SSH_CLIENT | cut -d' ' -f1` | sort"
```

Note, that is particularly useful for just about any port number. Remove the "watch" and create a crontab to log all of them.

(...coming soon...)


### Show number of connections to port 443 (webserver)

```
netstat -ntu | grep :443 | grep -v LISTEN | awk '{print $5}' | cut -d: -f1 | grep -v 127.0.0.1 | wc -l
```

