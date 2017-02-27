# HowTo: Port Introspection

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

