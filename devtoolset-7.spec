%global scl devtoolset-7
%scl_package %scl
%global df_toolchain d0e8f8ad24f38c3ad19cfb47cf1ba488a93de60d
%global df_perftools df416ac0951d00c1a35ef19bbef6d2f4af7c5883
%global df_toolchain_s %(c=%{df_toolchain}; echo ${c:0:7})
%global df_perftools_s %(c=%{df_perftools}; echo ${c:0:7})
%global dockerfiledir %{_datadir}/%{scl_prefix}dockerfiles

Summary: Package that installs %scl
Name: %scl_name
Version: 7.0
Release: 2%{?dist}
License: GPLv2+
Group: Applications/File
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Source0: README
# The source for this package was pulled from upstream's git.  Use the
# following commands to generate the tarball:
# git clone git://pkgs.devel.redhat.com/rpms/devtoolset-6-toolchain-docker -b devtoolset-6.0-rhel-7
# rm -rf devtoolset-6-toolchain-docker/.git{,ignore}
# tar cf - devtoolset-6-toolchain-docker | bzip2 -9 > devtoolset-6-toolchain-docker-%{df_toolchain_s}.tar.bz2
# git clone git://pkgs.devel.redhat.com/rpms/devtoolset-6-perftools-docker -b devtoolset-6.0-rhel-7
# rm -rf devtoolset-6-perftools-docker/.git{,ignore}
# tar cf - devtoolset-6-perftools-docker | bzip2 -9 > devtoolset-6-perftools-docker-%{df_perftools_s}.tar.bz2
Source1: devtoolset-6-toolchain-docker-%{df_toolchain_s}.tar.bz2
Source2: devtoolset-6-perftools-docker-%{df_perftools_s}.tar.bz2

# The base package requires just the toolchain and the perftools.
Requires: %{scl_prefix}toolchain %{scl_prefix}perftools
Obsoletes: %{name} < %{version}-%{release}

BuildRequires: scl-utils-build >= 20120927-11
BuildRequires: iso-codes
BuildRequires: help2man

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Group: Applications/File
Requires: scl-utils >= 20120927-11
Obsoletes: %{name}-runtime < %{version}-%{release}
Requires(post): libselinux policycoreutils-python
Requires(postun): libselinux policycoreutils-python
Requires(preun): libselinux policycoreutils-python

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: scl-utils-build >= 20120927-11
Obsoletes: %{name}-build < %{version}-%{release}

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package toolchain
Summary: Package shipping basic toolchain applications
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: %{scl_prefix}gcc %{scl_prefix}gcc-c++ %{scl_prefix}gcc-gfortran
Requires: %{scl_prefix}binutils %{scl_prefix}gdb %{scl_prefix}strace
Requires: %{scl_prefix}dwz %{scl_prefix}elfutils %{scl_prefix}memstomp
Requires: %{scl_prefix}ltrace %{scl_prefix}make
Obsoletes: %{name}-toolchain < %{version}-%{release}

%description toolchain
Package shipping basic toolchain applications (compiler, debugger, ...)

%package perftools
Summary: Package shipping performance tools
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: %{scl_prefix}oprofile %{scl_prefix}systemtap %{scl_prefix}valgrind
%ifarch x86_64 ppc64
Requires: %{scl_prefix}dyninst
%endif
Obsoletes: %{name}-perftools < %{version}-%{release}

%description perftools
Package shipping performance tools (systemtap, oprofile)

%package dockerfiles
Summary: Package shipping Dockerfiles for Developer Toolset
Group: Applications/File
Requires: gcc

%description dockerfiles
This package provides a set of example Dockerfiles that can be used
with Red Hat Developer Toolset.  Use these examples to stand up
test environments using the Docker container engine.

%package all
Summary: Package shipping all available toolsets.
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: %{scl_prefix}toolchain %{scl_prefix}perftools
Requires: rust-toolset-7 llvm-toolset-7 go-toolset-7
Obsoletes: %{name}-all < %{version}-%{release}

%description all
Package shipping all available toolsets (GCC toolchain, perftools,
Rust, LLVM, Go).

%package rust
Summary: Package shipping the Rust toolset
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: rust-toolset-7
Obsoletes: %{name}-rust < %{version}-%{release}

%description rust
Package shipping the Rust toolset.

%package llvm
Summary: Package shipping the LLVM toolset
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: llvm-toolset-7
Obsoletes: %{name}-llvm < %{version}-%{release}

%description llvm
Package shipping the LLVM toolset.

%package go
Summary: Package shipping the Go toolset
Group: Applications/File
Requires: %{scl_prefix}runtime
Requires: go-toolset-7
Obsoletes: %{name}-go < %{version}-%{release}

%description go
Package shipping the Go toolset.

%prep
%setup -c -T -a 1 -a 2

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat <<'EOF' | tee README
%{expand:%(cat %{SOURCE0})}
EOF

%build

# Temporary helper script used by help2man.
cat <<\EOF | tee h2m_helper
#!/bin/sh
if [ "$1" = "--version" ]; then
  printf '%%s' "%{?scl_name} %{version} Software Collection"
else
  cat README
fi
EOF
chmod a+x h2m_helper
# Generate the man page.
help2man -N --section 7 ./h2m_helper -o %{?scl_name}.7

# Enable collection script
# ========================
cat <<EOF >enable
# General environment variables
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
export INFOPATH=%{_infodir}\${INFOPATH:+:\${INFOPATH}}
export PCP_DIR=%{_scl_root}
# Some perl Ext::MakeMaker versions install things under /usr/lib/perl5
# even though the system otherwise would go to /usr/lib64/perl5.
export PERL5LIB=%{_scl_root}/%{perl_vendorarch}:%{_scl_root}/usr/lib/perl5:%{_scl_root}/%{perl_vendorlib}\${PERL5LIB:+:\${PERL5LIB}}
# bz847911 workaround:
# we need to evaluate rpm's installed run-time % { _libdir }, not rpmbuild time
# or else /etc/ld.so.conf.d files?
rpmlibdir=\$(rpm --eval "%%{_libdir}")
# bz1017604: On 64-bit hosts, we should include also the 32-bit library path.
if [ "\$rpmlibdir" != "\${rpmlibdir/lib64/}" ]; then
  rpmlibdir32=":%{_scl_root}\${rpmlibdir/lib64/lib}"
fi
export LD_LIBRARY_PATH=%{_scl_root}\$rpmlibdir\$rpmlibdir32\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
# duplicate python site.py logic for sitepackages
pythonvers=`python -c 'import sys; print sys.version[:3]'`
export PYTHONPATH=%{_prefix}/lib64/python\$pythonvers/site-packages:%{_prefix}/lib/python\$pythonvers/site-packages\${PYTHONPATH:+:\${PYTHONPATH}}
EOF

# Sudo script
# ===========
cat <<EOF >sudo
#! /bin/sh
# TODO: parse & pass-through sudo options from \$@
sudo_options="-E"

for arg in "\$@"
do
   case "\$arg" in
    *\'*)
      arg=`echo "\$arg" | sed "s/'/'\\\\\\\\''/g"` ;;
   esac
   cmd_options="\$cmd_options '\$arg'" 
done
exec /usr/bin/sudo \$sudo_options LD_LIBRARY_PATH=\$LD_LIBRARY_PATH PATH=\$PATH scl enable %{scl} "\$cmd_options"
EOF

# " (Fix vim syntax coloring.)

%install
(%{scl_install})

# This allows users to build packages using DTS.
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config << EOF
%%enable_devtoolset7 %%global ___build_pre %%{___build_pre}; source scl_source enable %{scl} || :
EOF

mkdir -p %{buildroot}%{_scl_root}/etc/alternatives %{buildroot}%{_scl_root}/var/lib/alternatives

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 sudo %{buildroot}%{_bindir}/

# Other directories that should be owned by the runtime
install -d -m 755 %{buildroot}%{_datadir}/appdata
# Otherwise unowned perl directories
install -d -m 755 %{buildroot}%{_libdir}/perl5
install -d -m 755 %{buildroot}%{_libdir}/perl5/vendor_perl
install -d -m 755 %{buildroot}%{_libdir}/perl5/vendor_perl/auto

%if 0%{?rhel} >= 7
install -d %{buildroot}%{dockerfiledir}
install -d -p -m 755 %{buildroot}%{dockerfiledir}/rhel7
collections="devtoolset-6-toolchain-docker devtoolset-6-perftools-docker"
for d in $collections; do
  install -d -p -m 755 %{buildroot}%{dockerfiledir}/rhel7/$d
  cp -a $d %{buildroot}%{dockerfiledir}/rhel7
done
%endif

# Install generated man page.
install -d -m 755 %{buildroot}%{_mandir}/man7
install -p -m 644 %{?scl_name}.7 %{buildroot}%{_mandir}/man7/

%files
%doc README
%{_mandir}/man7/%{?scl_name}.*

%files runtime
%scl_files
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_sysconfdir}/selinux-equiv.created
%dir %{_scl_root}/etc/alternatives
%dir %{_datadir}/appdata

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}*

%files toolchain

%files perftools

%files all

%files llvm

%files rust

%files go

%if 0%{?rhel} >= 7
%files dockerfiles
%{dockerfiledir}
%endif

%post runtime
if [ ! -f %{_sysconfdir}/selinux-equiv.created ]; then
  /usr/sbin/semanage fcontext -a -e / %{_scl_root}
  restorecon -R %{_scl_root}
  touch %{_sysconfdir}/selinux-equiv.created
fi

%preun runtime
[ $1 = 0 ] && rm -f %{_sysconfdir}/selinux-equiv.created || :

%postun runtime
if [ $1 = 0 ]; then
  /usr/sbin/semanage fcontext -d %{_scl_root}
  [ -d %{_scl_root} ] && restorecon -R %{_scl_root} || :
fi

%changelog
* Wed Jun  7 2017 Marek Polacek <polacek@redhat.com> - 7.0-2
- update %files for the recently added subpackages

* Wed Jun  7 2017 Marek Polacek <polacek@redhat.com> - 7.0-1
- add devtoolset-7-{go,llvm,rust,all} subpackages

* Thu May 25 2017 Marek Polacek <polacek@redhat.com> - 7.0-0
- initial version, with old dockerfiles (#1455129)
