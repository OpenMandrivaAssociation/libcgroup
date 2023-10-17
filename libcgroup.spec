%define _disable_rebuild_configure 1
%define major 3
%define mname cgroup
%define oldlibname %mklibname %{mname} 1
%define libname %mklibname %{mname}
%define devname %mklibname %{mname} -d

Summary:	Tools and libraries to control and monitor control groups
Name:		lib%{mname}
Group:		System/Base
Version:	3.1.0
Release:	1
License:	LGPLv2+
URL:		https://github.com/libcgroup/libcgroup
Source0:	https://github.com/libcgroup/libcgroup/archive/refs/tags/v3.1.0.tar.gz
Source1:	cgconfig.service
Patch0:		fedora-config.patch
Patch1:		libcgroup-0.37-chmod.patch
Patch2:		https://src.fedoraproject.org/rpms/libcgroup/blob/rawhide/f/libcgroup-0.40.rc1-coverity.patch
Patch3:		https://src.fedoraproject.org/rpms/libcgroup/blob/rawhide/f/libcgroup-0.40.rc1-fread.patch
Patch4:		https://src.fedoraproject.org/rpms/libcgroup/blob/rawhide/f/libcgroup-0.40.rc1-templates-fix.patch
BuildRequires:	pam-devel
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	coreutils
BuildRequires:	systemd-macros
BuildRequires:	gtest-source
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
%rename %{oldlibname}

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
%autosetup -p1
cp -a %{_prefix}/src/googletest .
sed -i -e 's,^git,# git,;s,^cmake,# cmake,;s,^make,# make,' bootstrap.sh
./bootstrap.sh

%build
%configure \
	--disable-daemon \
	--enable-opaque-hierarchy="name=systemd" \
	--enable-systemd

%make_build

%install
%make_install

# install config files
install -m644 samples/config/cgconfig.conf -D %{buildroot}%{_sysconfdir}/cgconfig.conf
install -m644 samples/config/cgconfig.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/cgconfig
install -m644 samples/config/cgsnapshot_*list.conf %{buildroot}/%{_sysconfdir}/

# sanitize pam module, we need only pam_cgroup.so in the right directory
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
%config(noreplace) %{_sysconfdir}/cgsnapshot_*list.conf
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
