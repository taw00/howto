# HowTo Rotate Log Files on a Linux System

**Scenario:** You have an application that generates log files. Those log files
can get out of hand (large) if something generates an event, or if the
application simply runs long enough.

**Solution:** Log rotation solves this problem. Based on rules (size or time
and number of backups) you can have the system keep a fixed set of log files
archived by copying the current log file, optionally compressing it, and then
truncating (starting over) the original log file.

For example, I can have a log file...

```
-rw-rw-r--. 1 todd todd 0 Mar 26 03:25 application.log
```

It starts off at 0 bytes big, but what if it explodes in size?

```
-rw-rw-r--. 1 todd todd 499586000 Mar 26 03:28 application.log
```

Holy cow! That file is now almost 500MB in size!

If I set my rules to log-rotate and compress that log file at 500MB, this will
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

**Assumptions for the example:** I am user "todd", I want my log file rotated
at 500KB (never allow that logfile to get bigger than that). And I want to keep
5 iterations but don't use a date extension. The log file lives in
`/home/todd/.myapplication/application.log`.

*Create log rotation configation file*

Use `sudo` or do this as the root user...

* Edit the file: `/etc/logrotate.d/toddsapplication`

```
/home/todd/.myapplication/application.log {
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

Save, and you are done!

That says, create new files as user `todd`, save only 5 of them, don't gripe if
the file does not exist, compress it, rotate at 500KB, and copy-then truncate.
We copy-then-truncate so that any running program actively writing to the file
does not hiccup.

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
    dateext
}
```

## Rotating daily, is just as simple...

*Changes demonstrated with example are:* We rotate the file daily, but not if
it is an empty log, and we create the archives with permissions 600 for `todd`
user and `todd` group. Note, permissions remain the same as the original log
file unless you specifically change it with the create parameter.

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
    nodateext
}
```

## The limitations of logrotate

The logrotate function on your typical linux system only runs once per day at some
odd hour. So, that 500MB maximum will only be checked once per day. If you have a
very active system that can have wild swings in logging, you may want to set up a
cron-job to run every hour, or every 30 minutes to check those logs...

```
sudo crontab -e
```

And then add this line, save, and exit...

```
# Run logrotate every 30 minutes
*/30  *  *  *  *   root    /usr/sbin/logrotate /etc/logrotate.conf
```


## Pretty simple, right? 

It's really that simple though this only touches upon the extensive
configurability of logrotate. `man logrotate` for more detail.

Please feel free to send feedback or comment to <t0dd@protonmail.com>

