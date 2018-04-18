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
# Included will be (eventually)...
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
#   - docs
#   - license file
#   - man page (1 and 5)
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

%define sourceIsPrebuilt 0
%define targetIsProduction 0
%define productionIncludesSnapinfo 0
%define includeSnapinfo1 1
%define includeSnapinfo2 0
%define includeMinorbump 1

# 1.0
%define vermajor 1.0
# 1.0.1
%define verminor 1
# -
# 1 (production)
%define pkgrel 1
# 0 (pre-production)
%define pkgrel_preprod 0
# 0.1
%define extraver_preprod 1
# 0.1.testing
%define snapinfo1 testing
# 0.1.testing.20180414
%define snapinfo2 20180414
# 0.1.testing.20180414.rp -- rp = repackaged (pre-built)
%define snapshot_rp rp
# 0.1.testing.20180414.rp.[DIST].taw0
%define minorbump taw0

# You can/should use URLs for sources as well. That is beyond the scope of
# this document.
# https://fedoraproject.org/wiki/Packaging:SourceURL
# https://fedoraproject.org/wiki/Packaging:SourceURL
Source0: %{name}-%{version}.tar.gz
Source1: %{name}-%{vermajor}-contrib.tar.gz

# Most of the time, the build system can figure out the requires.
# But if you need something specific...
#Requires:
# BuildRequires indicates everything you need to build the RPM
BuildRequires: tree desktop-file-utils
# CentOS/RHEL/EPEL can't do "Suggests:"
%if 0%{?fedora:1}
#Suggests:
%endif

# obsolete fictitious previous version of package after a rename
Provides: spec-pattern = 0.9
Obsoletes: spec-pattern < 0.9

License: MIT
Group: Applications/Internet
URL: https://github.com/taw00/howto

#
# Build the version string
# Don't edit this
#
Version: %{vermajor}.%{verminor}

#
# Build the release string
# Don't edit this large section
#

# release numbers
%undefine _relbuilder_pt1
%if %{targetIsProduction}
  %define _pkgrel %{pkgrel}
  %define _relbuilder_pt1 %{pkgrel}
%else
  %define _pkgrel %{pkgrel_preprod}
  %define _extraver %{extraver_preprod}
  %define _relbuilder_pt1 %{_pkgrel}.%{_extraver}
%endif

# snapinfo pt1
%undefine _snapinfo
%undefine _snapinfo1
%undefine _snapinfo2
%if %{includeSnapinfo1}
  %if %{targetIsProduction}
    %if %{productionIncludesSnapinfo}
      %define _snapinfo1 %{snapinfo1}
    %endif
  %else
    %define _snapinfo1 %{snapinfo1}
  %endif
%endif

%if %{includeSnapinfo2}
  %if %{targetIsProduction}
    %if %{productionIncludesSnapinfo}
      %define _snapinfo2 %{snapinfo2}
    %endif
  %else
    %define _snapinfo2 %{snapinfo2}
  %endif
%endif

%if 0%{?_snapinfo1:1}
  %if 0%{?_snapinfo2:1}
    %define _snapinfo %{_snapinfo1}.%{_snapinfo2}
  %else
    %define _snapinfo %{_snapinfo1}
  %endif
%else
  %if 0%{?_snapinfo2:1}
    %define _snapinfo %{_snapinfo2}
  %endif
%endif

# snapinfo finalized, to include repackage (pre-built) indicator
%undefine _relbuilder_pt2
%if %{sourceIsPrebuilt}
  %if 0%{?_snapinfo:1}
    %define _relbuilder_pt2 %{_snapinfo}.%{snapshot_rp}
  %else
    %define _relbuilder_pt2 %{snapshot_rp}
  %endif
%else
  %if 0%{?_snapinfo:1}
    %define _relbuilder_pt2 %{_snapinfo}
  %endif
%endif

# put it all together
# pt1 will always be defined. pt2 and minorbump may not be
%if ! %{includeMinorbump}
  %undefine minorbump
%endif
%define _release %{_relbuilder_pt1}
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
#   srcroot               specpattern-1.0
#      \_srccodetree        \_specpattern-1.0.1
#      \_srccontribtree     \_specpattern-1.0-contrib
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
# Prep section starts us in directory .../BUILD (_builddir)
#
# References (the docs for this universally suck):
# * http://ftp.rpm.org/max-rpm/s1-rpm-inside-macros.html
# * http://rpm.org/user_doc/autosetup.html
# * autosetup -q and setup -q leave out the root directory.
# I create a root dir and place the source and contribution trees under it.
# Extracted source tree structure (extracted in .../BUILD)
#   srcroot               specpattern-1.0
#      \_srccodetree        \_specpattern-1.0.1
#      \_srccontribtree     \_specpattern-1.0-contrib

mkdir %{srcroot}
# sourcecode
%setup -q -T -D -a 0 -n %{srcroot}
# contrib
%setup -q -T -D -a 1 -n %{srcroot}

# Libraries ldconfig file - we create it, because lib or lib64
echo "%{_libdir}/%{name}" > %{srccontribtree}/etc-ld.so.conf.d_%{name}.conf

# For debugging purposes...
cd .. ; /usr/bin/tree -df -L 1 %{srcroot} ; cd -


%build
# This section starts us in directory .../<_builddir>/<srcroot>

# I do this for all npm processed applications...
# Clearing npm's cache will hopefully elminate SHA1 integrity issues.
#/usr/bin/npm cache clean --force
#rm -rf ../.npm/_cacache
#rm -f %{srccodetree}/package-lock.json

# <insert program building instructions here>


%install
# This section starts us in directory .../<_builddir>/<srcroot>

# Create directories
install -d %{buildroot}%{_libdir}/%{name}
install -d -m755 -p %{buildroot}%{_bindir}
install -d %{buildroot}%{installtree}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_sysconfdir}/ld.so.conf.d

#cp -a %%{srccodetree}/%%{linuxunpacked}/* %%{buildroot}%%{installtree}

# a little ugly - symbolic link creation
#ln -s %%{installtree}/%%{name} %%{buildroot}%%{_bindir}/%%{name}

install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.16x16.png   %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.22x22.png   %{buildroot}%{_datadir}/icons/hicolor/22x22/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.24x24.png   %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.32x32.png   %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.48x48.png   %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.128x128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.256x256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.hicolor.svg         %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.16x16.png   %{buildroot}%{_datadir}/icons/HighContrast/16x16/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.22x22.png   %{buildroot}%{_datadir}/icons/HighContrast/22x22/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.24x24.png   %{buildroot}%{_datadir}/icons/HighContrast/24x24/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.32x32.png   %{buildroot}%{_datadir}/icons/HighContrast/32x32/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.48x48.png   %{buildroot}%{_datadir}/icons/HighContrast/48x48/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.128x128.png %{buildroot}%{_datadir}/icons/HighContrast/128x128/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.256x256.png %{buildroot}%{_datadir}/icons/HighContrast/256x256/apps/%{name}.png
install -D -m644 -p %{srccontribtree}/desktop/%{name}.highcontrast.svg         %{buildroot}%{_datadir}/icons/HighContrast/scalable/apps/%{name}.svg

install -D -m644 -p %{srccontribtree}/desktop/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# TODO... this doesn't see right... installtree?
#install -D -m755 -p %%{buildroot}%%{installtree}/libffmpeg.so %%{buildroot}%%{_libdir}/%%{name}/libffmpeg.so
#install -D -m755 -p %%{buildroot}%%{installtree}/libnode.so %%{buildroot}%%{_libdir}/%%{name}/libnode.so
install -D -m644 -p %{srccontribtree}/etc-ld.so.conf.d_%{name}.conf %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf


%files
%defattr(-,root,root,-)
%license %{srccodetree}/LICENSE
# We own /usr/share/specpattern and everything under it...
%{installtree}
%{_datadir}/icons/*
%{_datadir}/applications/%{name}.desktop
#%%{_bindir}/*
/etc/ld.so.conf.d/%{name}.conf
%dir %attr(755,root,root) %{_libdir}/%{name}
#%%{_libdir}/%%{name}/libffmpeg.so
#%%{_libdir}/%%{name}/libnode.so
#%%{_docsdir}/*
#%%{_mandir}/*


%post
umask 007
/sbin/ldconfig > /dev/null 2>&1


%postun
umask 007
/sbin/ldconfig > /dev/null 2>&1


#%clean
## Once needed if you are building on old RHEL/CentOS.
## No longer used.
#rm -rf %{buildroot}


%changelog
* Sat Apr 14 2018 Todd Warner <t0dd@protonmail.com> 1.0.1-0.1.testing.taw0
- Initial test build.
