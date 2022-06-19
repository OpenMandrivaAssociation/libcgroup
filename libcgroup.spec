%define major 1
%define mname cgroup
%define libname %mklibname %{mname} %{major}
%define devname %mklibname %{mname} -d

Summary:	Tools and libraries to control and monitor control groups
Name:		lib%{mname}
Group:		System/Base
Version:	0.41
Release:	10
License:	LGPLv2+
URL:		http://libcg.sourceforge.net/
Source0:	http://downloads.sourceforge.net/libcg/%{name}/v%{version}/%{name}-%{version}.tar.bz2
Source1:	cgconfig.service
Patch0:		fedora-config.patch
Patch1:		libcgroup-0.37-chmod.patch
Patch2:		libcgroup-0.40.rc1-coverity.patch
Patch3:		libcgroup-0.40.rc1-fread.patch
Patch4:		libcgroup-0.40.rc1-templates-fix.patch
Patch5:		libcgroup-0.41-lex.patch
Patch6:		libcgroup-0.41-api.c-support-for-setting-multiline-values-in-contro.patch
Patch7:		libcgroup-0.41-api.c-fix-order-of-memory-subsystem-parameters.patch
Patch8:		libcgroup-0.41-api.c-preserve-dirty-flag.patch
Patch9:		libcgroup-0.41-change-cgroup-of-threads.patch
Patch10:	libcgroup-0.41-fix-infinite-loop.patch
Patch11:	libcgroup-0.41-prevent-buffer-overflow.patch
Patch12:	libcgroup-0.41-tasks-file-warning.patch
Patch13:	libcgroup-0.41-fix-log-level.patch
Patch14:	libcgroup-0.41-size-of-controller-values.patch
BuildRequires:	pam-devel
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	coreutils
BuildRequires:	systemd-macros
# For _pre_groupadd
BuildRequires:	rpm-helper
Requires(pre):	shadow

%description
Control groups infrastructure. The tools and library to manipulate, control,
administrate and monitor control groups and the associated controllers.

%package -n %{mname}
Summary:	Tools to control and monitor control groups 
Group:		System/Base
Provides:	%{name} = %{version}-%{release}
Requires(post):	rpm-helper
Requires(preun):	rpm-helper

%description -n	cgroup
Control groups infrastructure. The tools to manipulate, control, administrate
and monitor control groups and the associated controllers.

%package -n pam_%{mname}
Summary:	A Pluggable Authentication Module for libcgroup
Group:		System/Libraries
Requires:	%{libname} = %{version}-%{release}

%description -n	pam_%{mname}
Linux-PAM module, which allows administrators to classify the user's login
processes to pre-configured control group.

%package -n %{libname}
Summary:	Libraries to control and monitor control groups
Group:		System/Libraries
# binaries are statically linked, so while they don't require the library,
# anything linked against the library will require the config files etc.
# rovided by the main package
Requires:	%{mname} = %{version}-%{release}

%description -n	%{libname}
Control groups infrastructure. The library to manipulate, control, administrate
and monitor control groups and the associated controllers.

%package -n %{devname}
Summary:	Development libraries to develop applications that utilize control groups
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
It provides API to create/delete and modify cgroup nodes. It will also in the
future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup -q
%patch0 -p1 -b .config-patch
%patch1 -p1 -b .chmod
%patch2 -p1 -b .coverity
%patch3 -p1 -b .fread
%patch4 -p1 -b .templates-fix
%patch5 -p2 -b .lex
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

%build
%ifarch %{ix86}
export CC=gcc
export CXX=g++
%endif

%configure \
	--disable-daemon \
	--enable-opaque-hierarchy="name=systemd"

%make_build

%install
%make_install

# install config files
install -m644 samples/cgconfig.conf -D %{buildroot}%{_sysconfdir}/cgconfig.conf
install -m644 samples/cgconfig.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/cgconfig
install -m644 samples/cgsnapshot_blacklist.conf %{buildroot}/%{_sysconfdir}/cgsnapshot_blacklist.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
rm -f %{buildroot}%{_libdir}/security/pam_cgroup.so
mv -f %{buildroot}%{_libdir}/security/pam_cgroup.so.*.*.* %{buildroot}%{_libdir}/security/pam_cgroup.so
rm -f %{buildroot}%{_libdir}/security/pam_cgroup.so.*
rm -f %{buildroot}%{_libdir}/security/pam_cgroup.la

# install unit and sysconfig files
install -d %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/
install -d %{buildroot}%{_sysconfdir}/sysconfig

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-libcgroup.preset << EOF
enable cgconfig.service
EOF

rm -f %{buildroot}%{_mandir}/man5/cgred.conf.5*
rm -f %{buildroot}%{_mandir}/man5/cgrules.conf.5*
rm -f %{buildroot}%{_mandir}/man8/cgrulesengd.8*

%pre -n %{mname}
%_pre_groupadd cgred

%files -n %{mname}
%config(noreplace) %{_sysconfdir}/sysconfig/cgconfig
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgsnapshot_blacklist.conf
%{_presetdir}/86-libcgroup.preset
%{_unitdir}/cgconfig.service
%{_bindir}/*
%{_mandir}/man[158]/*.[158]*

%files -n pam_%{mname}
%{_libdir}/security/pam_cgroup.so

%files -n %{libname}
%{_libdir}/lib%{mname}.so.%{major}
%{_libdir}/lib%{mname}.so.%{major}.*

%files -n %{devname}
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/lib%{mname}.so
