# HowTo Schedule a Nightly YUM or DNF Downloud of RPM Packages After Hours

**Scenario:** Fedora Linux machine that has a daily influx of RPM packages
(patches).

**Problem:** I have bandwidth constraints from 8am to 10pm every day in my
region.

**Solution:** Set up a cronjob (a job scheduler) to download all those RPMs
after hours.

RPM based linux machines are patched with RPM packages downloaded from the
internet. Sometimes these RPMs can be relatively large. Management of these
RPMs is down using a utility called DNF on newer linux distributions (Fedora
Linux, SUSE, etc) and YUM on older linuxes (namely CentOS 7 and RHEL 7).

If you are on a desktop machine running GNOME, there is a GUI software manager
that can also install these RPMs. It is essentially a wrapper around DNF.

Let's solve our problem. You can do it one of two ways...

_**Assumptions:**_

* You have to perform these actions as the root user directly or indirectly via
  `sudo`. My examples use `sudo`.
* You know how to use the `vi` editor. That's what the commands assume.
* `crontab -e` is how you schedule things. The process is...  
  _Edit crontab &xrarr; Save &xrarr; Exit &xrarr; Changes applied_
* Read more about crontab here: https://github.com/taw00/howto/blob/master/howto-schedule-cron-jobs-to-run-at-random-intervals.md

_**CentOS 7 or RHEL 7 Linux - Extra step**_

Install the yum downloader plugin:

```
sudo yum install yum-plugin-downloadonly
```


**Method1:** Download the RPM packages after hours. Install them later.

* Edit crontab:

   ```
   sudo crontab -e
   ```

* Set a schedule for 2:30am every day to download all available packages.
  Remember the format for crontab entries is...  
  _mins hours day-of-month month day-of-week command-or-script_

   ```
   # I'm a Fedora Linux machine...
   30 2 * * * /usr/bin/dnf upgrade --downloadonly -y --refresh
   # I'm a CentOS 7 or RHEL 7 machine...
   #30 2 * * * /usr/bin/yum update --downloadonly -y --refresh
   ```

   Save that and exit...

   ```
   :w
   :q
   ```

   You are scheduled! List your work...

   ```
   sudo crontab -l
   ```

* Install at your convenience (the next day, for example)...  
  _There may have potentially been additional packages made available between
  the time you downloaded them an when you trigger the actual update, but the
  difference should be much smaller. There are ways to offline update, but I
  leave figuring that out as an exercise for the reader._

  ```
  # I'm a Fedora Linux machine...
  sudo dnf upgrade
  # I'm a CentOS 7 or RHEL 7 machine...
  #sudo yum update
  ```

  If you just want to list what you have available...

  ```
  sudo dnf list
  # Or for CentOS/RHEL...
  #sudo yum list
  ```

**Method2:** Download and install the RPM packages after hours.

Just do the same thing, but remove the `--downloadonly` option from the
commandline.


**Troubleshooting:**

You can see your cron activity in the logs via...

```
sudo journalctl /usr/sbin/crond | tail -n 100
```

That is one example. I leave it up to the reader to figure out more ways to
look at the Journaling logs and how CentOS and RHEL probably do it differently.

