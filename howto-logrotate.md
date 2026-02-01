# HowTo Rotate Log Files on a Linux System

**Scenario:** You have an application that generates log files. Those log files
can get out of hand (large) if something generates an event, or if the
application simply runs long enough.

**Solution:** Log rotation helps mitigate this problem. Based on rules (size,
time, and number of archived backups) you can have the system keep a fixed set
of log files archived. This is done by copying the current log file, optionally
compressing it, and then truncating the original log file.

For example, I can have a log file...

```
-rw-rw-r--. 1 todd todd 0 Mar 26 03:25 application.log
```

It starts off at 0 bytes big, but what if it explodes in size?

```
-rw-rw-r--. 1 todd todd 499586000 Mar 26 03:28 application.log
```

Holy cow! That file is now almost 500MB in size!

If I set my rules to rotate and compress that log file at 500MB, this will
happen when the logrotate service next runs...

```
-rw-rw-r--. 1 todd todd 0 Mar 26 03:35 application.log
-rw-rw-r--. 1 todd todd 234967 Mar 26 03:35 application.log.1.gz
```

That application.log.1.gz contains the entire log, compressed with gzip, and
the application now has a fresh log file to write to. And if I set the rules
to only keep 5 archives, that .1 will eventually have a .2, .3, etc. archived
along side it. But at the 5 iteration, the original log file is deleted. The
log file is "rotated"

Note: On some systems, a date extension is commonly the default, so you will
have a datestamp instead of that .1, .2.

## Setting up the typical scenario

**Assumptions for this next example:** I am user "todd", I want my log file
rotated at 500KB (take action if the log file grows bigger than that). And I
want to keep 5 iterations (rotate 5) and use an integer file extension
(nodateext) instead of a date-formatted file extension. Finally, the log file
lives in `/home/todd/.myapplication/application.log`.

*Create log rotation configuration file*

Use `sudo` or do this as the root user...

Edit the file: `/etc/logrotate.d/toddsapplication`

```
/home/todd/.myapplication/application.log {
    su todd todd
    rotate 5
    missingok
    notifempty
    compress
    maxsize 500k
    #maxsize 1M
    #maxsize 10M
    #maxsize 50M
    #maxsize 500M
    copytruncate
    nodateext
}
```

Save, and you are done!

This configuration says: Create new files as user `todd`; save only 5 of them;
don't gripe if the file does not exist; compress it; rotate at 500KB; and
copy-then truncate.  We copy-then-truncate so that any running program actively
writing to the file does not hiccup.

> _IMPORTANT NOTE: That 500KB value is purely arbitrary. You may want to wait
> and see what the size of a log file is for a typical day of operations before
> you configure rotating them. And then multiply that by 5 or 10. For example,
> if my application generates 5MB of log data everyday, maybe I will set
> `maxsize 50M`. Or just pick a setting and adjust it over time through
> experience. It's something to think about._

...

Let's say this application has two log files, you can create two stanzas in
that logrotate configuration file, or combine them like this...

```
/home/todd/.myapplication/application.log /home/todd/.myapplication/debug.log {
    su todd todd
    rotate 5
    missingok
    notifempty
    compress
    maxsize 500k
    copytruncate
    nodateext
}
```

## Rotating daily, is just as simple...

*Changes demonstrated with example are:* We rotate the file daily, but not if
it is an empty log, and we create the archives with permissions 600 for `todd`
user and `todd` group. Note, permissions remain the same as the original log
file unless you specifically change it with the create parameter. Oh, and even
if the logrotate checks more than once a day, if that logfile gets bigger than
500KB, rotate it anyway.

```
/home/todd/.myapplication/application.log /home/todd/.myapplication/debug.log {
    daily
    notifempty
    create 600 todd todd
    rotate 5
    missingok
    notifempty
    compress
    maxsize 500k
    copytruncate
    dateext
}
```

And of course, if you only need to rotate the logs `weekly` or `monthly`, then
just adjust the settings appropriately.

## The limitations of logrotate

The logrotate function on your typical linux system only runs once per day at
some odd hour (like 3am or some such). So, that 500KB maximum in the first
example would only be checked once per day. If you have a very active system
that can have wild swings in logging, you may want to set up a cron-job to run
every hour, or every 30 minutes to check those logs...

```
sudo crontab -e
# ...or if you don't like the defaul editor, use this...
sudo EDITOR="nano" crontab -e
```

And then add this line; save; and exit...

```
# Run logrotate every 30 minutes
*/30  *  *  *  *   root    /usr/sbin/logrotate /etc/logrotate.conf
```


## Pretty simple, right? 

It's really that simple though this only touches upon the extensive
configurability of logrotate. `man logrotate` for more detail.

Comments and feedback  
—Todd Warner <a href="https://forms.gle/ogCeqcdqNSogYkPU8">(google contact form)</a>

