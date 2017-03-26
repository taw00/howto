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

### DuckDuckGo

<https://duckduckgo.com/?q=what+is+my+ip&ia=answer>

### icanhazip.com

<https://icanhazip.com>

An acquaintence of mine (Major Hayden) runs this simple website that so many
people use.

```
curl https://icanhazip.com/
# or curl -4 https://icanhazip.com/
```

This webservice provides a lot more functionality than appears on the surface.
Check it out: <https://major.io/icanhazip-com-faq/>

For example, "I want my IPv6 IP address..."

```
curl -6 https://icanhazip.com/
```

### SSH into a box and "look back at yourself"

```
# On most systems you can use $SSH_CLIENT as well
ssh <some user>:<some machine> 'echo $SSH_CONNECTION | cut -d" " -f1'
```


### ifconfig and 'ip addr show'

You can look at what you system thinks its IP address is. But this is not
reliable because it may have an internal IP and an external IP. That being
said, for many setups, if your system's internal and external IP are one and
the same, this quick and dirty...

```
ifconfig | grep -w inet | grep -v 127.0.0.1 | awk '{print $2}'
ifconfig | grep -w inet6 | grep -v ::1 | awk '{print $2}'
```

```
ip addr show | grep -w inet | grep -v 127.0.0.1 | awk '{print $2}' | cut -d"/" -f1
ip addr show | grep -w inet6 | grep -v ::1 | awk '{print $2}' | cut -d"/" -f1
```

---


## What's my MAC address?

```
ifconfig | grep -w ether | awk '{print $2}'
ip addr show | grep -w ether | awk '{print $2}'
```

---


## What's my network device name?

```
ip addr show | grep -w inet | grep -v 127.0.0.1 | awk '{print $NF}'
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

