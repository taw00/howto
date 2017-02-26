# HowTo: Schedule Cron Jobs to Run at Random Intervals

Let's say I wanted to run a cronjob in a random interval, for example, every 3
to 5 minutes. Or every 1 to 20 minutes. Or some other random interval. It's not
hard, lemme show you...

## Editing your crontab

But first, let's talk about editing your crontab. Every user has their own
crontab file where each configured line says "run this command on this date and
time". There are several ways to work with cron, but a user's crontab is the
most straight-forward mechanism.

Working with cron is this process: _Edit crontab. Save. Exit. Changes are
applied._ Changes do not take effect until after you exit the editor.

You edit your personal crontab configuration file with a specially built
workflow process. To edit with `contab -e`. Then you make your changes and
save+exit.

> Note: crontab usually uses `vi` as it's editor, or whatever the EDITOR
> environment variable is set to. If you don't like the default choice, use a
> different one with, for example, `EDITOR=gedit crontab -e` or
> `EDITOR=nano crontab -e`

## The basics of each line (scheduled job) in crontab

Crontab executes things on a schedule. Every line in the crontab file
represents a scheduled event. You CANNOT split things between lines. They all
operate asynchronous to each other. If you want to do something really really
complicated, write a script instead, and then execute that script from your
crontab.

The format: I am not going to go into great detail here &mdash;read `man 5 crontab` instead&mdash; but
the general format of a crontab entry is...

*mins hours day-of-month month day-of-week command-or-script*

For example, I want to send the date to a log file every minute...

```
* * * * * date >> $HOME/date.log 2>&1
```

Each of those `*`'s means "every" -- every minute, hour, day-of-month, etc...

For example, if I wanted to write the current date and time a log file every 3
minutes...

```
*/3 * * * * date >> $HOME/date.log 2>&1
```

## Adding random intervals

How would I make it execute randomly every 3 to 5 minutes?<br />
_For this example, we also demonstrate using a logfile variable. Note, the
present working directory is $HOME (your home directory), but you can't use
$variables except on the commandline. Therefore, in this example, if we
redirect to just $logfile, it will write to $HOME/$logfile._

```
logfile=date.log
t0to180secs="RANDOM % 181"
*/3 * * * * r=$(($t0to180secs)) ; sleep ${r}s ; date >> $logfile 2>&1 
```


How would I execute a command at a random day of the week at midnight?

```
logfile=date.log
tday0_to_day6="RANDOM % 6"
00 00 * * 0 r=$(($tday0_to_day6)) ; sleep ${r}d ; date >> $logfile 2>&1
```

## Fancy Fancy!

How about that random 3 to 5 minutes example, but with MUCH fancier logging?

```
logfile=date.log
m0="----Job scheduled -- pid:"
m1="----Job started ---- pid:"
m2="----Job completed -- pid:"
dformat="%b %d %T UTC"
t0to180secs="RANDOM % 181"
*/3 * * * * { date --utc +"$dformat $m0 $$" && r=$(($t0to180secs)) ; sleep ${r}s ; date --utc +"$dformat $m1 $$" && date && echo "Hello there!" --utc +"$dformat $m2 $$" ; } >> $logfile 2>&1 
```

---

## Good luck!

I hope this was of help. Send comments and feedback to <t0dd@protonmail.com>

---

## Bonus -- testing in a cron-like environment

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

Now test your commandline. Your environment is identical to what cron runs
within.
