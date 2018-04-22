# HowTo Package an Application as an RPM and Build It Using Mock

This HowTo is not written yet, but I have created a fully realized example
specfile (and source files). I use this template (or pattern) all the time
to wrap appplications into an RPM.

This example spec and source include:

- working simple commandline application -- a bash while loop
- working simple gnome-terminal application -- while loop in a terminal
- working simple daemon -- daemonized while loop
- working simple system service -- daemonized while loop that writes to journal
- systemd service configuration that will use email alerts if set up appropriately  
  (I will describe that process eventually)
- logrotation example configuration (though we don't log anything yet)
- firewalld application example definition file (though we don't use a port)
- everyhing placed in fairly "best practice" locations

Look for more documentation soon.

