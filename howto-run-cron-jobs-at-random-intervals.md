# HowTo Run Cron Jobs at Random Intervals

Let's say I wanted to run a cronjob in a random interval, for example, every 3
to 5 minutes. Or every 1 to 20 minutes. Or some other random interval. It's not
hard, lemme show you...

## Editing your crontab

But first, let's talk about editing your crontab. Every user has their own
crontab that says "run this command on this date and time". There are several
ways to work with cron, but a user's crontab is the most straight-forward
mechanism.

Working with cron is this process: _Edit crontab. Save. Exit. Changes are
applied._ Changes do not take effect until after you exit the editor.

So, edit your personal crontab with `contab -e`. Make your changes and then save+exit.

> Note: crontab usually uses `vi` as it's editor, or whatever the EDITOR
> environment variable is set to. If you don't like the default choice, use a
> different one with, for example, `EDITOR=gedit crontab -e` or
> `EDITOR=nano crontab -e`

## The basic scheduled and crontab line

Crontab executes things on a schedule. Every line in the crontab file is a new scheduled
event. You CANNOT split things between lines. They all operate asynchronous to each other.
If you want to do something really really complicated, write a script, and then execute
that script from your crontab.

The format: I am not going to go into great detail here &mdash;read `man 5 crontab` instead&mdash; but
the general format of a crontab entry is...

*mins hours day-of-month month day-of-week command-or-script*

For example, I want to send the date to a log file every minute...

```
* * * * * date >> $HOME/date.log 2>&1
```

Each of those `*`'s means "every" -- every minute, hour, day-of-month, etc...

How about if I wanted to send the date to a log file every 3 minutes...

```
*/3 * * * * date >> $HOME/date.log 2>&1
```

## Adding random intervals

So, how do I make it execute every 3 to 5 minutes?<br />
_For this example, we use a logfile variable. Note, the present working
directory is $HOME (your home directory), but you can't use $variables except
on the commandline. Therefore, in this example, if we redirect to just
$logfile, it will write to $HOME/$logfile._

```
logfile=date.log
t0to180secs="RANDOM % 181"
*/3 * * * * r=$(($t0to180secs)) ; sleep ${r}s ; date >> $logfile 2>&1 
```


How about a random day of the week at midnight?

```
logfile=date.log
tday0_to_day6="RANDOM % 6"
00 00 * * 0 r=$(($tday0_to_day6)) ; sleep ${r}d ; date >> $logfile 2>&1
```

## Fancy Fancy!

How about from 3 to 5 minutes, but with MUCH fancier logging?

```
# Note, current working directory is your home directory
logfile=date.log
m0="----Job scheduled -- pid:"
m1="----Job started ---- pid:"
m2="----Job completed -- pid:"
dformat="%b %d %T UTC"
t0to180secs="RANDOM % 181"
*/3 * * * * { date --utc +"$dformat $m0 $$" && r=$(($t0to180secs)) ; sleep ${r}s ; date --utc +"$dformat $m1 $$" && date && echo "Hello there!" --utc +"$dformat $m2 $$" ; } >> $logfile 2>&1 
```

---

Good luck! I hope this was of help. Comments and feedback to <t0dd@protonmail.com>
