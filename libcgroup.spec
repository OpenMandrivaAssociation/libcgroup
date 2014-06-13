%define	major	1
%define	mname	cgroup
%define	libname	%mklibname %{mname} %{major}
%define	devname	%mklibname %{mname} -d

Summary:	Tools and libraries to control and monitor control groups
Name:		lib%{mname}
Group:		System/Base
Version:	0.38
Release:	7
License:	LGPLv2+
URL:		http://libcg.sourceforge.net/
Source0:	http://downloads.sourceforge.net/libcg/%{name}/v%{version}/%{name}-%{version}.tar.bz2
Source1:	cgconfig.service
Source2:	cgred.service
Source3:	cgred.sysconfig
Source4:	libcgroup-README.Mandriva
Patch0:		libcgroup-fedora-config.patch
BuildRequires:	pam-devel
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	coreutils
Requires(pre):	shadow-utils

%description
Control groups infrastructure. The tools and library to manipulate, control,
administrate and monitor control groups and the associated controllers.

%package -n	%{mname}
Summary:	Tools to control and monitor control groups 
Group:		System/Base
Provides:	%{name} = %{version}-%{release}
Requires(post):	rpm-helper
Requires(preun): rpm-helper

%description -n	cgroup
Control groups infrastructure. The tools to manipulate, control, administrate
and monitor control groups and the associated controllers.

%package -n	pam_%{mname}
Summary:	A Pluggable Authentication Module for libcgroup
Group:		System/Libraries
Requires:	%{libname} = %{version}-%{release}

%description -n	pam_%{mname}
Linux-PAM module, which allows administrators to classify the user's login
processes to pre-configured control group.

%package -n	%{libname}
Summary:	Libraries to control and monitor control groups
Group:		System/Libraries
# binaries are statically linked, so while they don't require the library,
# anything linked against the library will require the config files etc.
# rovided by the main package
Requires:	%{mname} = %{version}-%{release}

%description -n	%{libname}
Control groups infrastructure. The library to manipulate, control, administrate
and monitor control groups and the associated controllers.

%package -n	%{devname}
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
%patch0 -p1 -b .config

cp %{SOURCE4} README.OpenMandriva

%build
%configure2_5x	--bindir=/bin \
		--sbindir=/sbin \
		--libdir=/%{_lib} \
		--enable-opaque-hierarchy="name=systemd"
%make

%install
rm -rf %{buildroot}
%makeinstall_std

# install config files
install -m644 samples/cgconfig.conf -D %{buildroot}%{_sysconfdir}/cgconfig.conf
install -m644 samples/cgconfig.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/cgconfig
install -m644 samples/cgrules.conf -D %{buildroot}%{_sysconfdir}/cgrules.conf
install -m644 samples/cgsnapshot_blacklist.conf %{buildroot}/%{_sysconfdir}/cgsnapshot_blacklist.conf



# sanitize pam module, we need only pam_cgroup.so in the right directory
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.so
mv -f %{buildroot}/%{_lib}/security/pam_cgroup.so.*.*.* %{buildroot}/%{_lib}/security/pam_cgroup.so
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.so.*
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.la

# install unit and sysconfig files
install -d %{buildroot}%{_unitdir}
install -m 644 %SOURCE1 %{buildroot}%{_unitdir}/
install -m 644 %SOURCE2 %{buildroot}%{_unitdir}/
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %SOURCE3 %{buildroot}%{_sysconfdir}/sysconfig/cgred

# move the devel stuff to /usr
mkdir -p %{buildroot}%{_libdir}
mv -f %{buildroot}/%{_lib}/lib%{mname}.la %{buildroot}%{_libdir}
rm -f %{buildroot}/%{_lib}/lib%{mname}.so
ln -sf ../../%{_lib}/lib%{mname}.so.%{major} %{buildroot}%{_libdir}/lib%{mname}.so

# pkgconfig file as well
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mv -f %{buildroot}/%{_lib}/pkgconfig/%{name}.pc %{buildroot}%{_libdir}/pkgconfig

# For now we will keep this, but this will be moved to /sys/fs/cgroup in later versions
# pre-create /cgroup directory
mkdir -p %{buildroot}/cgroup

%post -n %{mname}
%_post_service cgred
%_post_service cgconfig

%preun -n %{mname}
%_preun_service cgconfig
%_preun_service cgred

%files -n %{mname}
%doc README_daemon README.OpenMandriva
%dir /cgroup
%config(noreplace) %{_sysconfdir}/sysconfig/cgred
%config(noreplace) %{_sysconfdir}/sysconfig/cgconfig
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
%config(noreplace) %{_sysconfdir}/cgsnapshot_blacklist.conf
%{_mandir}/man[158]/*.[158]*
%{_unitdir}/cgconfig.service
%{_unitdir}/cgred.service
/bin/cgclassify
/bin/cgcreate
/bin/cgdelete
/bin/cgexec
/bin/cgget
/bin/cgset
/bin/cgsnapshot
/bin/lscgroup
/bin/lssubsys
/sbin/cgclear
/sbin/cgconfigparser
/sbin/cgrulesengd

%files -n pam_%{mname}
/%{_lib}/security/pam_cgroup.so

%files -n %{libname}
/%{_lib}/lib%{mname}.so.%{major}
/%{_lib}/lib%{mname}.so.%{major}.*

%files -n %{devname}
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/lib%{mname}.so

