%define	major	1
%define	mname	cgroup
%define	libname	%mklibname %{mname} %{major}
%define	devname	%mklibname %{mname} -d

Summary:	Tools and libraries to control and monitor control groups
Name:		lib%{mname}
Group:		System/Base
Version:	0.37.1
Release:	%mkrel 2
License:	LGPLv2+
URL:		http://libcg.sourceforge.net/
Source0:	http://downloads.sourceforge.net/libcg/%{name}/v%{version}/%{name}-%{version}.tar.bz2
Source1:	libcgroup-README.Mandriva
Patch0:		libcgroup-fedora-config.patch
Patch1:		libcgroup-0.36.2-systemd.patch
Patch2:		libcgroup-0.37.1-systemd.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-%{release}-buildroot
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
%patch1 -p1
%patch2 -p1

cp %{SOURCE1} README.Mandriva

%build
%configure2_5x	--bindir=/bin \
		--sbindir=/sbin \
		--libdir=/%{_lib} \
		--enable-initscript-install
%make

%install
rm -rf %{buildroot}
%makeinstall_std

# install config files
install -m644 samples/cgred.conf -D %{buildroot}%{_sysconfdir}/sysconfig/cgred.conf
install -m644 samples/cgconfig.conf -D %{buildroot}%{_sysconfdir}/cgconfig.conf
install -m644 samples/cgconfig.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/cgconfig
install -m644 samples/cgrules.conf -D %{buildroot}%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.so
mv -f %{buildroot}/%{_lib}/security/pam_cgroup.so.*.*.* %{buildroot}/%{_lib}/security/pam_cgroup.so
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.so.*
rm -f %{buildroot}/%{_lib}/security/pam_cgroup.la

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

%clean
rm -rf %{buildroot}

%post -n %{mname}
%_post_service cgred
%_post_service cgconfig

%preun -n %{mname}
%_preun_service cgconfig
%_preun_service cgred

%files -n %{mname}
%defattr(-,root,root)
%doc README_daemon README.Mandriva
%dir /cgroup
%config(noreplace) %{_sysconfdir}/sysconfig/cgred.conf
%config(noreplace) %{_sysconfdir}/sysconfig/cgconfig
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
%{_mandir}/man[158]/*.[158]*
%attr(755,root,root) %{_initrddir}/cgconfig
%attr(755,root,root) %{_initrddir}/cgred
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
%defattr(-,root,root)
/%{_lib}/security/pam_cgroup.so

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/lib%{mname}.so.%{major}
/%{_lib}/lib%{mname}.so.%{major}.*

%files -n %{devname}
%defattr(-,root,root)
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/lib%{mname}.so

