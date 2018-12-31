%define bdbv 5.3.28
%global selinux_variants mls strict targeted

%if 0%{?_no_gui:1}
%define _buildqt 0
%define buildargs --with-gui=no
%else
%define _buildqt 1
%if 0%{?_use_qt4}
%define buildargs --with-qrencode --with-gui=qt4
%else
%define buildargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:		mazacoin
Version:	0.12.0
Release:	2%{?dist}
Summary:	Peer to Peer Cryptographic Currency

Group:		Applications/System
License:	MIT
URL:		https://mazacoin.net/
Source0:	https://github.com/mazaska/mazacoin/releases/download/v%{version}/mazacoin-%{version}.tar.gz
Source1:	http://download.oracle.com/berkeley-db/db-%{bdbv}.NC.tar.gz

Source10:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/debian/examples/mazacoin.conf

#man pages
Source20:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/debian/manpages/mazacoind.1
Source21:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/debian/manpages/mazacoin-cli.1
Source22:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/debian/manpages/mazacoin-qt.1
Source23:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/debian/manpages/mazacoin.conf.5

#selinux
Source30:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/rpm/mazacoin.te
# Source31 - what about mazacoin-tx and bench_mazacoin ???
Source31:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/rpm/mazacoin.fc
Source32:	https://raw.githubusercontent.com/mazaska/mazacoin/v%{version}/contrib/rpm/mazacoin.if

Source100:	https://upload.wikimedia.org/wikipedia/commons/4/46/Bitcoin.svg

%if 0%{?_use_libressl:1}
BuildRequires:	libressl-devel
%else
BuildRequires:	openssl-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	miniupnpc-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	libevent-devel


Patch0:		mazacoin-0.12.0-libressl.patch


%description
Mazacoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of mazacoins is carried out collectively by the network.

%if %{_buildqt}
%package core
Summary:	Peer to Peer Cryptographic Currency
Group:		Applications/System
Obsoletes:	%{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
%if 0%{?_use_qt4}
BuildRequires:	qt-devel
%else
BuildRequires:	qt5-qtbase-devel
# for /usr/bin/lrelease-qt5
BuildRequires:	qt5-linguist
%endif
BuildRequires:	protobuf-devel
BuildRequires:	qrencode-devel
BuildRequires:	%{_bindir}/desktop-file-validate
# for icon generation from SVG
BuildRequires:	%{_bindir}/inkscape
BuildRequires:	%{_bindir}/convert

%description core
Mazacoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of mazacoins is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Mazacoin wallet, this is probably the package you want.
%endif


%package libs
Summary:	Mazacoin shared libraries
Group:		System Environment/Libraries

%description libs
This package provides the bitcoinconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:	Development files for mazacoin
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
bitcoinconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package server
Summary:	The mazacoin daemon
Group:		System Environment/Daemons
Requires:	mazacoin-utils = %{version}-%{release}
Requires:	selinux-policy policycoreutils-python
Requires(pre):	shadow-utils
Requires(post):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
Requires(postun):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
BuildRequires:	systemd
BuildRequires:	checkpolicy
BuildRequires:	%{_datadir}/selinux/devel/Makefile

%description server
This package provides a stand-alone mazacoin-core daemon. For most users, this
package is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
mazacoin-core node they use to connect to the network.

If you use the graphical mazacoin-core client then you almost certainly do not
need this package.

%package utils
Summary:	Mazacoin utilities
Group:		Applications/System

%description utils
This package provides several command line utilities for interacting with a
mazacoin-core daemon.

The mazacoin-cli utility allows you to communicate and control a mazacoin daemon
over RPC, the mazacoin-tx utility allows you to create a custom transaction, and
the bench_mazacoin utility can be used to perform some benchmarks.

This package contains utilities needed by the mazacoin-server package.


%prep
%setup -q
%patch0 -p1 -b .libressl
cp -p %{SOURCE10} ./mazacoin.conf.example
tar -zxf %{SOURCE1}
cp -p db-%{bdbv}.NC/LICENSE ./db-%{bdbv}.NC-LICENSE
mkdir db4 SELinux
cp -p %{SOURCE30} %{SOURCE31} %{SOURCE32} SELinux/


%build
CWD=`pwd`
cd db-%{bdbv}.NC/build_unix/
../dist/configure --enable-cxx --disable-shared --with-pic --prefix=${CWD}/db4
make install
cd ../..

./autogen.sh
%configure LDFLAGS="-L${CWD}/db4/lib/" CPPFLAGS="-I${CWD}/db4/include/" --with-miniupnpc --enable-glibc-back-compat %{buildargs}
make %{?_smp_mflags}

pushd SELinux
for selinuxvariant in %{selinux_variants}; do
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
	mv mazacoin.pp mazacoin.pp.${selinuxvariant}
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
done
popd


%install
make install DESTDIR=%{buildroot}

mkdir -p -m755 %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/mazacoind %{buildroot}%{_sbindir}/mazacoind

# systemd stuff
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/mazacoin.conf
d /run/mazacoind 0750 mazacoin mazacoin -
EOF
touch -a -m -t 201504280000 %{buildroot}%{_tmpfilesdir}/mazacoin.conf

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/mazacoin
# Provide options to the mazacoin daemon here, for example
# OPTIONS="-testnet -disable-wallet"

OPTIONS=""

# System service defaults.
# Don't change these unless you know what you're doing.
CONFIG_FILE="%{_sysconfdir}/mazacoin/mazacoin.conf"
DATA_DIR="%{_localstatedir}/lib/mazacoin"
PID_FILE="/run/mazacoind/mazacoind.pid"
EOF
touch -a -m -t 201504280000 %{buildroot}%{_sysconfdir}/sysconfig/mazacoin

mkdir -p %{buildroot}%{_unitdir}
cat <<EOF > %{buildroot}%{_unitdir}/mazacoin.service
[Unit]
Description=Mazacoin daemon
After=syslog.target network.target

[Service]
Type=forking
ExecStart=%{_sbindir}/mazacoind -daemon -conf=\${CONFIG_FILE} -datadir=\${DATA_DIR} -pid=\${PID_FILE} \$OPTIONS
EnvironmentFile=%{_sysconfdir}/sysconfig/mazacoin
User=mazacoin
Group=mazacoin

Restart=on-failure
PrivateTmp=true
TimeoutStopSec=120
TimeoutStartSec=60
StartLimitInterval=240
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF
touch -a -m -t 201504280000 %{buildroot}%{_unitdir}/mazacoin.service
#end systemd stuff

mkdir %{buildroot}%{_sysconfdir}/mazacoin
mkdir -p %{buildroot}%{_localstatedir}/lib/mazacoin

#SELinux
for selinuxvariant in %{selinux_variants}; do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 SELinux/mazacoin.pp.${selinuxvariant} %{buildroot}%{_datadir}/selinux/${selinuxvariant}/mazacoin.pp
done

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/mazacoin.ico %{buildroot}%{_datadir}/pixmaps/mazacoin.ico
install -p share/pixmaps/nsis-header.bmp %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/nsis-wizard.bmp %{buildroot}%{_datadir}/pixmaps/
install -p %{SOURCE100} %{buildroot}%{_datadir}/pixmaps/mazacoin.svg
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/mazacoin16.png -w16 -h16
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/mazacoin32.png -w32 -h32
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/mazacoin64.png -w64 -h64
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/mazacoin128.png -w128 -h128
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/mazacoin256.png -w256 -h256
%{_bindir}/convert -resize 16x16 %{buildroot}%{_datadir}/pixmaps/mazacoin256.png %{buildroot}%{_datadir}/pixmaps/mazacoin16.xpm
%{_bindir}/convert -resize 32x32 %{buildroot}%{_datadir}/pixmaps/mazacoin256.png %{buildroot}%{_datadir}/pixmaps/mazacoin32.xpm
%{_bindir}/convert -resize 64x64 %{buildroot}%{_datadir}/pixmaps/mazacoin256.png %{buildroot}%{_datadir}/pixmaps/mazacoin64.xpm
%{_bindir}/convert -resize 128x128 %{buildroot}%{_datadir}/pixmaps/mazacoin256.png %{buildroot}%{_datadir}/pixmaps/mazacoin128.xpm
%{_bindir}/convert %{buildroot}%{_datadir}/pixmaps/mazacoin256.png %{buildroot}%{_datadir}/pixmaps/mazacoin256.xpm
touch %{buildroot}%{_datadir}/pixmaps/*.png -r %{SOURCE100}
touch %{buildroot}%{_datadir}/pixmaps/*.xpm -r %{SOURCE100}

# Desktop File - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/mazacoin-core.desktop
[Desktop Entry]
Encoding=UTF-8
Name=Mazacoin
Comment=Mazacoin P2P Cryptocurrency
Comment[fr]=Mazacoin, monnaie virtuelle cryptographique pair à pair
Comment[tr]=Mazacoin, eşten eşe kriptografik sanal para birimi
Exec=mazacoin-qt %u
Terminal=false
Type=Application
Icon=mazacoin128
MimeType=x-scheme-handler/mazacoin;
Categories=Office;Finance;
EOF
# change touch date when modifying desktop
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/applications/mazacoin-core.desktop
%{_bindir}/desktop-file-validate %{buildroot}%{_datadir}/applications/mazacoin-core.desktop

# KDE protocol - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/kde4/services
cat <<EOF > %{buildroot}%{_datadir}/kde4/services/mazacoin-core.protocol
[Protocol]
exec=mazacoin-qt '%u'
protocol=mazacoin
input=none
output=none
helper=true
listing=
reading=false
writing=false
makedir=false
deleting=false
EOF
# change touch date when modifying protocol
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/kde4/services/mazacoin-core.protocol
%endif

# man pages
install -D -p %{SOURCE20} %{buildroot}%{_mandir}/man1/mazacoind.1
install -p %{SOURCE21} %{buildroot}%{_mandir}/man1/mazacoin-cli.1
%if %{_buildqt}
install -p %{SOURCE22} %{buildroot}%{_mandir}/man1/mazacoin-qt.1
%endif
install -D -p %{SOURCE23} %{buildroot}%{_mandir}/man5/mazacoin.conf.5

# nuke these, we do extensive testing of binaries in %%check before packaging
rm -f %{buildroot}%{_bindir}/test_*

%check
make check
pushd src
srcdir=. test/mazacoin-util-test.py
popd
qa/pull-tester/rpc-tests.py -extended

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre server
getent group mazacoin >/dev/null || groupadd -r mazacoin
getent passwd mazacoin >/dev/null ||
	useradd -r -g mazacoin -d /var/lib/mazacoin -s /sbin/nologin \
	-c "Mazacoin wallet server" mazacoin
exit 0

%post server
%systemd_post mazacoin.service
# SELinux
if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
for selinuxvariant in %{selinux_variants}; do
	%{_sbindir}/semodule -s ${selinuxvariant} -i %{_datadir}/selinux/${selinuxvariant}/mazacoin.pp &> /dev/null || :
done
%{_sbindir}/semanage port -a -t mazacoin_port_t -p tcp 12832
%{_sbindir}/semanage port -a -t mazacoin_port_t -p tcp 12835
%{_sbindir}/semanage port -a -t mazacoin_port_t -p tcp 11832
%{_sbindir}/semanage port -a -t mazacoin_port_t -p tcp 11835
%{_sbindir}/fixfiles -R mazacoin-server restore &> /dev/null || :
%{_sbindir}/restorecon -R %{_localstatedir}/lib/mazacoin || :
fi

%posttrans server
%{_bindir}/systemd-tmpfiles --create

%preun server
%systemd_preun mazacoin.service

%postun server
%systemd_postun mazacoin.service
# SELinux
if [ $1 -eq 0 ]; then
	if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
	%{_sbindir}/semanage port -d -p tcp 12832
	%{_sbindir}/semanage port -d -p tcp 12835
	%{_sbindir}/semanage port -d -p tcp 11832
	%{_sbindir}/semanage port -d -p tcp 11835
	for selinuxvariant in %{selinux_variants}; do
		%{_sbindir}/semodule -s ${selinuxvariant} -r mazacoin &> /dev/null || :
	done
	%{_sbindir}/fixfiles -R mazacoin-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/mazacoin ] && \
		%{_sbindir}/restorecon -R %{_localstatedir}/lib/mazacoin &> /dev/null || :
	fi
fi

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files core
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING mazacoin.conf.example doc/README.md doc/bips.md doc/files.md doc/multiwallet-qt.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/mazacoin-qt
%attr(0644,root,root) %{_datadir}/applications/mazacoin-core.desktop
%attr(0644,root,root) %{_datadir}/kde4/services/mazacoin-core.protocol
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.svg
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/mazacoin-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files server
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING mazacoin.conf.example doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_sbindir}/mazacoind
%attr(0644,root,root) %{_tmpfilesdir}/mazacoin.conf
%attr(0644,root,root) %{_unitdir}/mazacoin.service
%dir %attr(0750,mazacoin,mazacoin) %{_sysconfdir}/mazacoin
%dir %attr(0750,mazacoin,mazacoin) %{_localstatedir}/lib/mazacoin
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/mazacoin
%attr(0644,root,root) %{_datadir}/selinux/*/*.pp
%attr(0644,root,root) %{_mandir}/man1/mazacoind.1*
%attr(0644,root,root) %{_mandir}/man5/mazacoin.conf.5*

%files utils
%defattr(-,root,root,-)
%license COPYING
%doc COPYING mazacoin.conf.example doc/README.md
%attr(0755,root,root) %{_bindir}/mazacoin-cli
%attr(0755,root,root) %{_bindir}/mazacoin-tx
%attr(0755,root,root) %{_bindir}/bench_mazacoin
%attr(0644,root,root) %{_mandir}/man1/mazacoin-cli.1*
%attr(0644,root,root) %{_mandir}/man5/mazacoin.conf.5*



%changelog
* Fri Feb 26 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-2
- Rename Qt package from mazacoin to mazacoin-core
- Make building of the Qt package optional
- When building the Qt package, default to Qt5 but allow building
-  against Qt4
- Only run SELinux stuff in post scripts if it is not set to disabled

* Wed Feb 24 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-1
- Initial spec file for 0.12.0 release

# This spec file is written from scratch but a lot of the packaging decisions are directly
# based upon the 0.11.2 package spec file from https://www.ringingliberty.com/bitcoin/
