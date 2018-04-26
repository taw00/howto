# specpattern.spec
#
# This SPEC file serves as a template --a typical usage pattern-- for how I
# create RPMs. The first iteration of this contained copious notes. I will
# strip all that out in favor of as clean of a spec file as possible.
#
# This is not a canonical howto, but it should be good enough to get you
# started. Let me know if you see any blatant errors or needed correction:
# t0dd@protonmail.com
#
# ---
#
# The pattern will build, dependent on your configuration...

# - Production (generally available or GA):
#     Source RPM (SRPM): specpattern-1.0.1-1.fc27.taw0.src.rpm
#     Binary RPM (RPM): specpattern-1.0.1-1.fc27.taw0.x86_64.rpm
# - Pre-production (testing, alpha, beta, rc, ...):
#     Source RPM (SRPM): specpattern-1.0.1-0.1.beta2.fc27.taw0.src.rpm
#     Binary RPM (RPM): specpattern-1.0.1-0.1.beta2.fc27.taw0.x86_64.rpm
# - Examples with extended snapinfo (date, git hash snippet, ...):
#     specpattern-1.0.1-0.1.beta2.20180414.fc27.taw0.src.rpm
#     specpattern-1.0.1-0.1.beta2.6bba08bgit.fc27.taw0.src.rpm
# - Examples of packaging from pre-built source archives...
#     specpattern-1.0.1-1.rp.fc27.taw0.src.rpm
#     specpattern-1.0.1-0.1.testing.rp.fc27.taw0.src.rpm
#     specpattern-1.0.1-0.1.beta2.6bba08bgit.rp.fc27.taw0.src.rpm

#
# I will bump the versions and release over time as I develop this pattern. You
# know, like a real package. :)
#
# ---
#
# Included will be...
# * a functional minimal application that can be installed on Fedora Linux,
#   CentOS, or RHEL.
# * package release flags
#   - flag for type of primary source (source code or binary pre-build)
#   - flag for type of target -- pre-production or production
#   - flag for snapinfo inclusion
#   - flag for minorbump inclusion
# * an executable
# * systemd stuff
#   - executable daemon
#   - configuration
#   - email upon start, stop, systemd-level configuration
# * documentation
#   - docs (eventually)
#   - license file
#   - man page (1 and 5) (eventually)
# * a filewalld configuration example
# * logrotation
# * application as desktop, to include menu icons and such (hicolor and
#   highcontrast)
#
# ---
#
# Further reading:
# * https://docs.fedoraproject.org/quick-docs/en-US/creating-rpm-packages.html
# * https://fedoraproject.org/wiki/Packaging:Guidelines?rd=Packaging/Guidelines
# * https://fedoraproject.org/wiki/packaging:versioning
# * https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard
# * https://developer.fedoraproject.org/deployment/rpm/about.html
# * https://rpm-packaging-guide.github.io/
# * http://rpm-guide.readthedocs.io/en/latest/
# * http://backreference.org/2011/09/17/some-tips-on-rpm-conditional-macros/
# * http://rpm5.org/docs/api/macros.html
# * https://fedoraproject.org/wiki/Licensing:Main
# * https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing
#
# A note about specfile comments:
# The percent sign + {variable} is a semantic for macro expansion. They are
# expanded even in comments. To escape them you double up the sign. Therefore
# all macro values will have their percent signs doubled in comments, example
# %%{variable}, but in practice they will only be used singularly.
#
# ---
#
# Package (RPM) name-version-release.
#
# <name>-<version>-<release>
# ...version is (can be many decimals):
# <vermajor>.<verminor>
# ...where release is:
# <pkgrel>[.<extraver>][.<snapinfo>].DIST[.<minorbump>]
# ...all together now:
# <name>-<vermajor.<verminor>-<pkgrel>[.<extraver>][.<snapinfo>].DIST[.<minorbump>]
#
# Note about the pattern for release iterations (ie. the release value of
# name-version-release):
#     If you are still in development, but the production package is expected
#     to have a release value of 8 (previous release was 7) for example, you
#     always work one step back (in the 7's) and add another significant digit.
#     I.e., release value of 7.1, 7.2, 7.3, etc... are all pre-production
#     release nomenclatures for an eventual release numbered at 8. When we go
#     into production, we "round up" and drop the decimal and probably all the
#     snapinfo as well.  specpattern-1.0.1-7.3.beta2 --> specpattern-1.0.1-8
#
# Source tarballs that I am using to create this...
# - specpattern-1.0.1.tar.gz
# - specpattern-1.0-contrib.tar.gz
#

Name: specpattern
Summary: Example application RPM package
#BuildArch: noarch

%define targetIsProduction 0
%define includeSnapinfo 1
%define includeMinorbump 1
%define sourceIsPrebuilt 0


# VERSION
# 1.0
%define vermajor 1.0
# 1.0.1
%define verminor 1
Version: %{vermajor}.%{verminor}


# RELEASE
# if production - "targetIsProduction 1"
%define pkgrel_prod 1

# if pre-production - "targetIsProduction 0"
# eg. 0.3.testing
%define pkgrel_preprod 0
%define extraver_preprod 4
%define snapinfo testing
#%%define snapinfo testing.20180424
#%%define snapinfo beta2.41d5c63.gh

# if sourceIsPrebuilt (rp=repackaged)
# eg. 1.rp (prod) or 0.3.testing.rp (pre-prod)
%define snapinfo_rp rp

# if includeMinorbump
%define minorbump taw0

# Building the release string (don't edit this)...

%if %{targetIsProduction}
  %if %{includeSnapinfo}
    %{warn:"Warning: target is production and yet you want snapinfo included. This is not typical."}
  %endif
%else
  %if ! %{includeSnapinfo}
    %{warn:"Warning: target is pre-production and yet you elected not to incude snapinfo (testing, beta, ...). This is not typical."}
  %endif
%endif

# release numbers
%undefine _relbuilder_pt1
%if %{targetIsProduction}
  %define _pkgrel %{pkgrel_prod}
  %define _relbuilder_pt1 %{pkgrel_prod}
%else
  %define _pkgrel %{pkgrel_preprod}
  %define _extraver %{extraver_preprod}
  %define _relbuilder_pt1 %{_pkgrel}.%{_extraver}
%endif

# snapinfo and repackage (pre-built) indicator
%undefine _relbuilder_pt2
%if ! %{includeSnapinfo}
  %undefine snapinfo
%endif
%if ! %{sourceIsPrebuilt}
  %undefine snapinfo_rp
%endif
%if 0%{?snapinfo_rp:1}
  %if 0%{?snapinfo:1}
    %define _relbuilder_pt2 %{snapinfo}.%{snapinfo_rp}
  %else
    %define _relbuilder_pt2 %{snapinfo_rp}
  %endif
%else
  %if 0%{?snapinfo:1}
    %define _relbuilder_pt2 %{snapinfo}
  %endif
%endif

# put it all together
# pt1 will always be defined. pt2 and minorbump may not be
%define _release %{_relbuilder_pt1}
%if ! %{includeMinorbump}
  %undefine minorbump
%endif
%if 0%{?_relbuilder_pt2:1}
  %if 0%{?minorbump:1}
    %define _release %{_relbuilder_pt1}.%{_relbuilder_pt2}%{?dist}.%{minorbump}
  %else
    %define _release %{_relbuilder_pt1}.%{_relbuilder_pt2}%{?dist}
  %endif
%else
  %if 0%{?minorbump:1}
    %define _release %{_relbuilder_pt1}%{?dist}.%{minorbump}
  %else
    %define _release %{_relbuilder_pt1}%{?dist}
  %endif
%endif

Release: %{_release}
# ----------- end of release building section

# You can/should use URLs for sources as well. That is beyond the scope of
# this example.
# https://fedoraproject.org/wiki/Packaging:SourceURL
Source0: %{name}-%{version}.tar.gz
Source1: %{name}-%{vermajor}-contrib.tar.gz

# Most of the time, the build system can figure out the requires.
# But if you need something specific...
Requires: gnome-terminal

# BuildRequires indicates everything you need to build the RPM
# For desktop environments, you want to test the {name}.desktop file
# For mock environments I add vim-enhanced and less so I can introspect by hand
#BuildRequires: tree
BuildRequires: tree desktop-file-utils
#BuildRequires: tree desktop-file-utils vim-enhanced less

# CentOS/RHEL/EPEL can't do "Suggests:"
%if 0%{?fedora:1}
#Suggests:
%endif

# obsolete fictitious previous version of package after a rename
Provides: spec-pattern = 0.9
Obsoletes: spec-pattern < 0.9

License: MIT
URL: https://github.com/taw00/howto
# Group is deprecated. Don't use it. Left here as a reminder...
# https://fedoraproject.org/wiki/RPMGroups 
#Group: Unspecified

# CHANGE or DELETE this for your package
# System user for the systemd specpatternd.service.
# If you want to retain the systemd service configuration and you therefore
# change this, you will have to dig into the various -contrib configuration
# files to change things there as well. 
%define systemuser spuser
%define systemgroup spgroup


# If you comment out "debug_package" RPM will create additional RPMs that can
# be used for debugging purposes. I am not an expert at this, BUT ".build_ids"
# are associated to debug packages, and I have lately run into packaging
# conflicts because of them. This is a topic I can't share a whole lot of
# wisdom about, but for now... I turn all that off.
#
# How debug info and build_ids managed (I only halfway understand this):
# https://github.com/rpm-software-management/rpm/blob/master/macros.in
%define debug_package %{nil}
%define _unique_build_ids 1
%define _build_id_links alldebug

# https://fedoraproject.org/wiki/Changes/Harden_All_Packages
# https://fedoraproject.org/wiki/Packaging:Guidelines#PIE
%define _hardened_build 1

# Extracted source tree structure (extracted in .../BUILD)
#   srcroot               {name}-1.0
#      \_srccodetree        \_{name}-1.0.1
#      \_srccontribtree     \_{name}-1.0-contrib
%define srcroot %{name}-%{vermajor}
%define srccodetree %{name}-%{version}
%define srccontribtree %{name}-%{vermajor}-contrib
# /usr/share/specpattern
%define installtree %{_datadir}/%{name}


# RHEL5 and below need this defined.
#BuildRoot: %%{_topdir}/BUILDROOT/


%description
Example Application is just an example application. You can find it in your
desktop menus and there is even a systemd service called exampleappd that you
can start stop and restart. 


%prep
# CREATING RPM:
# - prep step (comes before build)
# - This step extracts all code archives and takes any preparatory steps
#   necessary prior to the build.
#
# Prep section starts us in directory .../BUILD (_builddir)
#
# References (the docs for this universally suck):
# * http://ftp.rpm.org/max-rpm/s1-rpm-inside-macros.html
# * http://rpm.org/user_doc/autosetup.html
# * autosetup -q and setup -q leave out the root directory.
# I create a root dir and place the source and contribution trees under it.
# Extracted source tree structure (extracted in .../BUILD)
#   srcroot               {name}-<vermajor>
#      \_srccodetree        \_{name}-<version>
#      \_srccontribtree     \_{name}-<vermajor>-contrib

mkdir %{srcroot}
# sourcecode
%setup -q -T -D -a 0 -n %{srcroot}
# contrib
%setup -q -T -D -a 1 -n %{srcroot}

# Libraries ldconfig file - we create it, because lib or lib64
echo "%{_libdir}/%{name}" > %{srccontribtree}/etc-ld.so.conf.d_%{name}.conf

# README message about the /var/lib/specpattern directory
echo "\
This directory only exists as an example data directory

The spuser home dir is here: /var/lib/%{name}
The systemd managed %{name} datadir is also here: /var/lib/%{name}
The %{name} config file is housed here: /etc/%{name}/%{name}.conf
" > %{srccontribtree}/systemd/var-lib-%{name}_README

# For debugging purposes...
cd .. ; /usr/bin/tree -df -L 1 %{srcroot} ; cd -


%build
# CREATING RPM:
# - build step (comes before install step)
# - This step performs any action that takes the code and turns it into a
#   runnable form. Usually by compiling.
#
# This section starts us in directory <_builddir>/<srcroot>

# I do this for all npm processed applications...
# Clearing npm's cache will hopefully elminate SHA1 integrity issues.
#/usr/bin/npm cache clean --force
#rm -rf ../.npm/_cacache
#rm -f %{srccodetree}/package-lock.json

## Man Pages - not used as of yet
#gzip %%{buildroot}%%{_mandir}/man1/*.1

cd %{srccodetree}
# <insert program building instructions here>


%install
# CREATING RPM:
# - install step (comes before files step)
# - This step moves anything needing to be part of the package into the
#   {buildroot}, therefore mirroring the final directory and file structure of
#   an installed RPM.
#
# This section starts us in directory <_builddir>/<srcroot>

# Cheatsheet for built-in RPM macros:
#   _bindir = /usr/bin
#   _sbindir = /usr/sbin
#   _datadir = /usr/share
#   _mandir = /usr/share/man
#   _sysconfdir = /etc
#   _localstatedir = /var
#   _sharedstatedir is /var/lib
#   _prefix = /usr
#   _libdir = /usr/lib or /usr/lib64 (depending on system)
#   https://fedoraproject.org/wiki/Packaging:RPMMacros
# These two are defined in RPM versions in newer versions of Fedora (not el7)
%define _tmpfilesdir /usr/lib/tmpfiles.d
%define _unitdir /usr/lib/systemd/system

# Create directories
install -d %{buildroot}%{_libdir}/%{name}
install -d -m755 -p %{buildroot}%{_bindir}
install -d -m755 -p %{buildroot}%{_sbindir}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_sysconfdir}/ld.so.conf.d
install -d %{buildroot}%{_tmpfilesdir}
install -d %{buildroot}%{_unitdir}
# /etc/specpattern/
install -d %{buildroot}%{_sysconfdir}/%{name}
# /var/lib/specpattern/...
install -d %{buildroot}%{_sharedstatedir}/%{name}
# /var/log/specpattern/
install -d -m750 %{buildroot}%{_localstatedir}/log/%{name}
# /etc/sysconfig/specpatternd-scripts/
install -d %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts
# /usr/share/specpattern/
install -d %{buildroot}%{installtree}

# Binaries - a little ugly - symbolic link creation
ln -s %{installtree}/%{name}-gnome-terminal.sh %{buildroot}%{_bindir}/%{name}
ln -s %{installtree}/%{name}-daemon.sh %{buildroot}%{_sbindir}/%{name}d
install -D -p %{srccodetree}/%{name}-gnome-terminal.sh %{buildroot}%{installtree}/%{name}-gnome-terminal.sh
install -D -p %{srccodetree}/%{name}-daemon.sh %{buildroot}%{installtree}/%{name}-daemon.sh
install -D -p %{srccodetree}/%{name}-process.sh %{buildroot}%{installtree}/%{name}-process.sh

# Desktop
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.16x16.png   %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.22x22.png   %{buildroot}%{_datadir}/icons/hicolor/22x22/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.24x24.png   %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.32x32.png   %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.48x48.png   %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.128x128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.256x256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.512x512.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.svg         %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.16x16.png   %{buildroot}%{_datadir}/icons/HighContrast/16x16/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.22x22.png   %{buildroot}%{_datadir}/icons/HighContrast/22x22/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.24x24.png   %{buildroot}%{_datadir}/icons/HighContrast/24x24/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.32x32.png   %{buildroot}%{_datadir}/icons/HighContrast/32x32/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.48x48.png   %{buildroot}%{_datadir}/icons/HighContrast/48x48/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.128x128.png %{buildroot}%{_datadir}/icons/HighContrast/128x128/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.256x256.png %{buildroot}%{_datadir}/icons/HighContrast/256x256/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.512x512.png %{buildroot}%{_datadir}/icons/HighContrast/512x512/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.svg         %{buildroot}%{_datadir}/icons/HighContrast/scalable/apps/%{name}.svg

install -D -m644 -p %{srccontribtree}/desktop/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# Libraries
#install -D -m755 -p %%{buildroot}%%{installtree}/libffmpeg.so %%{buildroot}%%{_libdir}/%%{name}/libffmpeg.so
#install -D -m755 -p %%{buildroot}%%{installtree}/libnode.so %%{buildroot}%%{_libdir}/%%{name}/libnode.so
install -D -m644 -p %{srccontribtree}/etc-ld.so.conf.d_%{name}.conf %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf

## Man Pages - not used as of yet
#install -d %%{buildroot}%%{_mandir}
#install -D -m644 %%{srccodetree}/share/man/man1/* %%{buildroot}%%{_mandir}/man1/

## Bash completion
#install -D -m644 %%{srccontribtree}/bash/%%{name}.bash-completion  %%{buildroot}%%{_datadir}/bash-completion/completions/%%{name}
#install -D -m644 %%{srccontribtree}/bash/%%{name}d.bash-completion %%{buildroot}%%{_datadir}/bash-completion/completions/%%{name}d

# Config
install -D -m640 %{srccontribtree}/systemd/etc-%{name}_%{name}.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -D -m644 %{srccontribtree}/systemd/etc-%{name}_%{name}.conf %{srccontribtree}/%{name}.conf.example

# README message about the /var/lib/specpattern directory
install -D -m644 %{srccontribtree}/systemd/var-lib-%{name}_README %{buildroot}%{_sharedstatedir}/%{name}/README

# System services
install -D -m600 -p %{srccontribtree}/systemd/etc-sysconfig_%{name}d %{buildroot}%{_sysconfdir}/sysconfig/%{name}d
install -D -m755 -p %{srccontribtree}/systemd/etc-sysconfig-%{name}d-scripts_%{name}d.send-email.sh %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.send-email.sh
install -D -m755 -p %{srccontribtree}/systemd/etc-sysconfig-%{name}d-scripts_%{name}d.config-file-check.sh %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.config-file-check.sh
install -D -m755 -p %{srccontribtree}/systemd/etc-sysconfig-%{name}d-scripts_%{name}d.write-to-journal.sh %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.write-to-journal.sh
install -D -m644 -p %{srccontribtree}/systemd/usr-lib-systemd-system_%{name}d.service %{buildroot}%{_unitdir}/%{name}d.service
install -D -m644 -p %{srccontribtree}/systemd/usr-lib-tmpfiles.d_%{name}d.conf %{buildroot}%{_tmpfilesdir}/%{name}d.conf

# Log files
# ...logrotate file rules
install -D -m644 -p %{srccontribtree}/logrotate/etc-logrotate.d_%{name} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
# ...ghosted log files - need to exist in the installed buildroot
touch %{buildroot}%{_localstatedir}/log/%{name}/debug.log

# Service definition files for firewalld for full nodes
install -D -m644 -p %{srccontribtree}/firewalld/usr-lib-firewalld-services_%{name}.xml %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml


%files
# CREATING RPM:
# - files step (final step)
# - This step makes a declaration of ownership of any listed directories
#   or files
# - The install step should have set permissions and ownership correctly,
#   but of final tweaking is often done in this section
#
%defattr(-,root,root,-)
%license %{srccodetree}/LICENSE

# The directories...
%defattr(-,%{systemuser},%{systemgroup},-)
# /etc/specpattern/
%dir %attr(750,%{systemuser},%{systemgroup}) %{_sysconfdir}/%{name}
# /var/lib/specpattern/...
%dir %attr(750,%{systemuser},%{systemgroup}) %{_sharedstatedir}/%{name}
%{_sharedstatedir}/%{name}/*
# /var/log/specpattern/...
%dir %attr(750,%{systemuser},%{systemgroup}) %{_localstatedir}/log/%{name}
# /etc/sysconfig/specpatternd-scripts/
%dir %attr(755,%{systemuser},%{systemgroup}) %{_sysconfdir}/sysconfig/%{name}d-scripts
# /usr/share/specpattern/
%dir %attr(755,%{systemuser},%{systemgroup}) %{_datadir}/%{name}
%defattr(-,root,root,-)
# /usr/[lib,lib64]/specpattern/
%dir %attr(755,root,root) %{_libdir}/%{name}

# Documentation
# no manpage examples yet
#%%{_mandir}/man1/*.1.gz
#%%{_docsdir}/*
# config example
%doc %{srccontribtree}/%{name}.conf.example


# Binaries
%{_bindir}/%{name}
%{_sbindir}/%{name}d
%defattr(-,%{systemuser},%{systemgroup},-)
%{_datadir}/%{name}/%{name}-process.sh
%{_datadir}/%{name}/%{name}-daemon.sh
%{_datadir}/%{name}/%{name}-gnome-terminal.sh
%defattr(-,root,root,-)

# systemd service definition
%{_unitdir}/%{name}d.service

# systemd service tmp file
%{_tmpfilesdir}/%{name}d.conf

# systemd service config and scripts
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/sysconfig/%{name}d
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.send-email.sh
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.config-file-check.sh
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}d-scripts/%{name}d.write-to-journal.sh

# application configuration when run as systemd service
%config(noreplace) %attr(640,%{systemuser},%{systemgroup}) %{_sysconfdir}/%{name}/%{name}.conf

# /var/lib/specpattern/README
%attr(640,%{systemuser},%{systemgroup}) %{_sharedstatedir}/%{name}/README

# firewalld service definition
%{_prefix}/lib/firewalld/services/%{name}.xml

# Desktop
%{_datadir}/icons/*
%{_datadir}/applications/%{name}.desktop

# Libraries
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
#%%{_libdir}/%%{name}/libffmpeg.so
#%%{_libdir}/%%{name}/libnode.so

# Logs
# log file - doesn't initially exist, but we still own it
%ghost %{_localstatedir}/log/%{name}/debug.log
%attr(644,root,root) %{_sysconfdir}/logrotate.d/%{name}



%pre
# INSTALLING THE RPM:
# - pre section (runs before the install process)
# - system users are added if needed. Any other roadbuilding.
#
# This section starts us in directory .../BUILD/<srcroot>
# Note that _sharedstatedir is /var/lib and /var/lib/specpattern will be the homedir
# for spuser
#
# This is for the case where you run specpattern as a service (systemctl start specpatternd)
getent group %{systemgroup} >/dev/null || groupadd -r %{systemgroup}
getent passwd %{systemuser} >/dev/null || useradd -r -g %{systemgroup} -d %{_sharedstatedir}/%{name} -s /sbin/nologin -c "System user '%{systemuser}' to isolate execution" %{systemuser}


%post
# INSTALLING THE RPM:
# - post section (runs after the install process is complete)
#
umask 007
# refresh library context
/sbin/ldconfig > /dev/null 2>&1
# refresh systemd context
test -e %{_sysconfdir}/%{name}/%{name}.conf && %systemd_post %{name}d.service
# refresh firewalld context
test -f %{_bindir}/firewall-cmd && firewall-cmd --reload --quiet || true


%postun
# UNINSTALLING THE RPM:
# - postun section (runs after an RPM has been removed)
#
umask 007
# refresh library context
/sbin/ldconfig > /dev/null 2>&1
# refresh firewalld context
test -f %{_bindir}/firewall-cmd && firewall-cmd --reload --quiet || true


#%clean
## Once needed if you are building on old RHEL/CentOS.
## No longer used.
#rm -rf %{buildroot}


%changelog
* Thu Apr 26 2018 Todd Warner <t0dd@protonmail.com> 1.0.1-0.4.testing.taw0
- cleanup - version and release build should all be together.

* Tue Apr 24 2018 Todd Warner <t0dd@protonmail.com> 1.0.1-0.3.testing.taw0
- Further simplified the snapinfo, minorbump, and repackage logic.
- Issue warnings if your production and snapinfo settings are atypical.

* Sun Apr 22 2018 Todd Warner <t0dd@protonmail.com> 1.0.1-0.2.testing.taw0
- Simplified the snapinfo logic.
- Updated the desktop icons.
- Added a simple little specpattern loop program that runs in a terminal or  
  is daemonized.
- Added systemd and firewalld service definitions. Added logrotation rules.
- Logs nicely to the journal.

* Sat Apr 14 2018 Todd Warner <t0dd@protonmail.com> 1.0.1-0.1.testing.taw0
- Initial test build.
