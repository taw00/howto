== HowTo: Set up a local yum/dnf RPM repository

_Note: This document is a work in progress and simply notes for the moment._

1. Create a directory for the repository: Example, ~/repo

```
cd ~
mkdir repo
```

Note: If you are sharing this with many users, you make want to do this as root and in the `/var` directory.

2. Install the tool needed to create repos...

```
sudo dnf install createrepo_c
```

3. Copy the RPMs you want to include in the repo, into the repo...

```
cp /path/to/rpms/*.rpm repo/
```

4. Create the repo metadata...

```
cd repo
createrepo_c .
```

And, of course, if you did this in `/var/repo` you will want to do this as root: `sudo createrepo_c .`

5. Create the yum .repo configuration file so that your linux system will now be
able to fetch things from that repository...

Using a text editor _as root_ create and edit `/etc/yum.repo_d/my-rpms.repo` and
add this text to it and then save...

```
[my-rpms]
name=My RPMs $releasever - $basearch
baseurl=/home/<USERNAME>/repo
enabled=1
metadata_expire=1d
gpgcheck=0
#gpgcheck=1
#gpgkey=file:///<path to GPG key>/key.asc
#gpgkey=https://<URL to GPG key>/key.asc
```

Save that.

Notes:

* Replace "<USERNAME>" with your username -- if using the `/var` directory, that
doesn't apply, of course.
* If you didn't sign your packages, make sure the "gpgcheck" flag is off.
Signing packages is beyond the scope of this document.

6. Check that it yum/dnf knows about your repository...

```
sudo dnf repolist
```

Your repository should show on in the list.


7. Install your RPM...

Note: For the first run, you will likely have to use the `--refresh` flag and
any time you add more RPMs and refresh that repository.

```
sudo dnf install the-rpm-i-want-to-install
```

8. Adding RPMs to that repository...

Just go through the same process, but from step 3 ownwards. To install anything
though you will definitely have to add `--refresh` to the `dnf install`
commandline unless you wait the time needed for the metadata to expire.

```
cd ~/repo
cp /path/to/new-rpms/*.rpm ./
createrepo_c .
sudo dnf install the-rpm-i-want-to-install --refresh
```

That is all there really is to it. You can also make RPMs from a `/var/repo`
repo available via HTTP. To do that, reference
<http://www.remotecto.net/2009/10/20/creating-a-local-and-http-redhat-yum-repository/>
will help you out.

Good luck!

