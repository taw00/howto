# HowTo Schedule Cron Jobs to Run at Random Intervals

Let's say I wanted to run a cronjob in a random interval, for example, every 3
to 5 minutes. Or every 1 to 20 minutes. Or some other random interval. It's not
hard, lemme show you...

## Editing your crontab

But first, let's talk about editing your crontab. Every user has their own
crontab file where each configured line says "run this command on this date and
time". There are several ways to work with cron, but a user's crontab is the
most straight-forward mechanism.

Working with cron is this process:<br />
&nbsp;&nbsp;&nbsp;&nbsp; _Edit crontab &xrarr; Save &xrarr; Exit &xrarr; Changes applied_<br />
Changes do not take effect until after you exit the editor.

You edit your personal crontab configuration file with a specially built
workflow process. To edit with, open up a terminal and type `crontab -e`. Then you make your changes and
save+exit.

> Note: crontab usually uses `vi` as its editor, or whatever the EDITOR
> environment variable is set to. If you don't like the default choice, use a
> different one with, for example, `EDITOR=vim crontab -e` or `EDITOR=gedit crontab -e` or
> `EDITOR=nano crontab -e` or `EDITOR=micro crontab -e` or whatever.

## The basics of each line (scheduled job) in crontab

Crontab executes things on a schedule. Every line in the crontab file
represents a scheduled event. You CANNOT split things between lines. They all
operate asynchronous to each other. If you want to do something really really
complicated, write a script instead, and then execute that script from your
crontab.

The format: I am not going to go into great detail here &mdash;read `man 5 crontab` instead&mdash; but
the general format of a crontab entry line is:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*mins hours day-of-month month day-of-week command-or-script*

For example, I want to send the date to a log file every minute...

```
* * * * * date >> $HOME/crontab-demo.log 2>&1
```

Each of those `*`'s means "every" -- every minute, hour, day-of-month, etc...

> For these examples, open another terminal and watch the demo logfile we are creating: `tail -F ~/crontab-demo.log`
>
> When this exercise is over, `CTL-C` to exit and feel free to delete the logfile.

For example, if I wanted to write the current date and time to a log file every 3
minutes...

```
*/3 * * * * date >> $HOME/crontab-demo.log 2>&1
```

...or at 3am and 5am...

```
* 3 * * * date >> $HOME/crontab-demo.log 2>&1
* 5 * * * date >> $HOME/crontab-demo.log 2>&1
```

...but since they were the same command, the syntax could be...

```
* 3,5 * * * date >> $HOME/crontab-demo.log 2>&1
```


## Adding random intervals

How would I make it execute randomly every 3 to 5 minutes?<br />
_For this example, we also demonstrate using a logfile variable. Note, the
present working directory is $HOME (your home directory), but you can't use
$variables except on the commandline. Therefore, in this example, if we
redirect to just $logfile, it will write to $HOME/$logfile._

```
logfile=crontab-demo.log
t0to180secs="RANDOM % 181"
*/3 * * * * r=$(($t0to180secs)) ; sleep ${r}s ; date >> $logfile 2>&1
```


How would I execute a command at a random day of the week at midnight?

```
logfile=crontab-demo.log
tday0_to_day6="RANDOM % 6"
00 00 * * 0 r=$(($tday0_to_day6)) ; sleep ${r}d ; date >> $logfile 2>&1
```

## Fancy Fancy!

How about that random 3 to 5 minutes example, but with MUCH fancier logging?

```
logfile=crontab-demo.log
m0="-- Job scheduled -- pid:"
m1="-- Job started ---- pid:"
m2="-- Job completed -- pid:"
# date formatting...
df="%b %d %T UTC"
t0to180secs="RANDOM % 181"
*/3 * * * * { date --utc +"$df $m0 $$" && r=$(($t0to180secs)) ; sleep ${r}s ; date --utc +"$df $m1 $$" && date && echo "Hello there!" --utc +"$df $m2 $$" ; } >> $logfile 2>&1
```

The result would looks something like this...

```
[taw00@demo ~]$ tail -F crontab-demo.log
Feb 26 15:51:01 UTC -- Job scheduled -- pid: 17144 (sleeping for 94s)
Feb 26 15:52:35 UTC -- Job started ---- pid: 17144
Hello there!
Feb 26 15:52:35 UTC -- Job completed -- pid: 17144
```

### Looking at the journal logs:

If you want to watch cronjobs kicking off in the journal logs, do this...
```
journalctl /usr/sbin/crond |tail -n100
# ...or...
journalctl /usr/sbin/crond -f
```

Do that as root or using `sudo`. I leave it to you, dear reader, to learn how
to work with journalctl with a bit more sophistication.

---

### This completes our little demonstration.

You can either wipe out the examples in your crontab or save them for future refence:  Just comment out any schedule lines in your crontab (with `#`), save, and exit. You now have a small reference for the next time you have to edit the crontab configuration.


### Feedback

I hope this was of help. Send comments and feedback to <t0dd@protonmail.com>

&nbsp;

&nbsp;

---

#### Bonus Tutorial &mdash; Testing in a cron-like environment

Wondering why your cron job is failing and can't quite figure it out? Set up a
duplicate environment and test your commandline.

```
crontab -e
```

Now add this to your crontab, scheduled for 1 minute after "right now". For
example, if it is currently, 14 minutes after midnight, I would schedule this
for 00:15...

```
15 00 * * * env > ~/cronenv
```

Save and exit.

Wait until 00:15 for that file to show up. And then...

```
env - `cat ~/cronenv` /bin/sh
```

Now test your commandline. Your environment is now identical to cron's.


