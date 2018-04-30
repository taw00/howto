# HowTo Package an Application as an RPM and Build It Using Mock

This HowTo is not really written yet, but I have created a fully realized
example specfile (and source files) demonstrating a very simple program (a
couple bash scripts). I use this RPM specfile template and source code
structure all the time to wrap appplications into an RPM.

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

Start browsing here: <https://github.com/taw00/howto/source/>  
In particular look at the specpattern RPM specfile found
here: <https://github.com/taw00/howto/source/SPECS/> and the source tarballs in
<https://github.com/taw00/howto/source/SOURCES/>.

The specfile is long-ish and noisy because of all the desktop icons and
whatnot, but this program is pretty straight forward once you dive in a bit.
I may make a super simplified version as well.

## Setting up your build environment

RPM? How? What?:
* <https://fedoraproject.org/wiki/How_to_create_an_RPM_package>  
  (read especially "Preparing your system")
* <https://github.com/rpm-software-management/mock/wiki>
* <https://fedoraproject.org/wiki/Packaging:Versioning>

In order to build from a source RPM, you first need to set up your environment.
If you have not already, _**do this as your normal user (not root)**_ from the
commandline:

```sh
# Install needed packages
sudo dnf install @development-tools rpmdevtools rpm-sign
# optional
#sudo dnf install fedora-packager
# create your working folder ~/rpmbuild/[SOURCES,SRPMS,SPECS,RPMS]
rpmdev-setuptree

# Add yourself to the mock group
# mock group membership allows you to build in mock build # environments
sudo usermod -a -G mock $USER
# refresh your login so that the new group shows up for this user
# (not as reliable as logging out and logging back in again)
newgrp -
```

***If that fails,*** you need to read more about setting up your development
environment at the link that was provided earlier.

Note, it suggests using a separate user on your system to build RPMs… you can
do that, but for our examples, I am assuming you are doing it with whatever
user you want. I execute these commands from my personal normal user account
usually.

**Configure mock**

Copy `/etc/mock/site-defaults.cfg` to `~/.config/mock.cfg`
```sh
mkdir -p ~/.config
cp -i /etc/mock/site-defaults.cfg ~/.config/mock.cfg
```
and then edit `~/.config/mock.cfg` and configure it similarly to this (this is
what I have uncommented and configured in mine.

```sh
# ~/.config/mock.cfg
config_opts['basedir'] = '/var/lib/mock/'
config_opts['cache_topdir'] = '/var/cache/mock'
config_opts['rpmbuild_networking'] = True
config_opts['bootstrap_module_enable'] = []
config_opts['bootstrap_module_install'] = []
config_opts['environment']['LANG'] = os.environ.setdefault('LANG', 'en_US.UTF-8')

# I use 'tree', 'vim', 'less' in my testing
config_opts['chroot_additional_packages'] = ['tree', 'vim-enhanced', 'less']

# I turn off "cleanup" when doing a lot of testing.
#config_opts['cleanup_on_success'] = 0
#config_opts['cleanup_on_failure'] = 0
```

## Building something with `mock`

Let's use this 'specpattern' RPM as an example (that's what it is here for).

1. Clone this github repo and cd into it...

```sh
git clone https://github.com/taw00/howto.git
cd howto/source/
```

2. Assemble a source RPM for Fedora 27

Note that you can see all available OS distibutions and architectures available here: `ls /etc/mock/`

```sh
mock -r fedora-27-x86_64 --buildsrpm --spec SPECS/specpattern.spec --sources SOURCES/ --resultdir ./tmp/
```

3. Build the binary RPM from that source RPM

```sh
# This filename is an example. Look in that 'tmp' directory for whatever
# .src.rpm you just assempted.
mock -r fedora-27-x86_64 ./tmp/specpattern-1.0.1-0.5.testing.fc27.taw0.src.rpm --sources SOURCES/ --resultdir tmp/
```

4. Examine the RPM you just built

```sh
# This filename is an example. Look in that 'tmp' directory for whatever
# binary rpm you just built.
rpm -qlp ./tmp/specpattern-1.0.1-0.5.testing.fc27.taw0.x86_64.rpm
```

5. Install it!

Note that I am assuming the package's build target matches the OS you are
running.

```sh
# This filename is an example. Look in that 'tmp' directory for whatever
# binary rpm you just built.
sudo dnf install  ./tmp/specpattern-1.0.1-0.5.testing.fc27.taw0.x86_64.rpm
```

6. All done with building stuff? Purge the mock environment and return
   everything back to a fairly pristine state...

```sh
mock --scrub all
```

Pretty slick. Mock allows you to build stuff without polluting your everyday environment.
