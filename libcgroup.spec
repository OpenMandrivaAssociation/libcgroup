%define	major	1
%define	mname	cgroup
%define	libname	%mklibname %{mname} %{major}
%define	devname	%mklibname %{mname} -d

Name:		libcgroup
Summary:	Tools and libraries to control and monitor control groups
Group:		System/Base
Version:	0.35
Release:	%mkrel 1
License:	LGPLv2+
URL:		http://libcg.sourceforge.net/
Source0:	http://downloads.sourceforge.net/libcg/%{name}-v%{version}.tar.bz2
Source1:	libcgroup-README.Mandriva
Patch0:		libcgroup-fedora-config.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-%{release}-buildroot
BuildRequires:	pam-devel
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	coreutils

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

%package	pam
Summary:	A Pluggable Authentication Module for libcgroup
Group:		System Environment/Base
Requires:	%{libname} = %{version}-%{release}

%description	pam
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
Requires:	%{mname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
It provides API to create/delete and modify cgroup nodes. It will also in the
future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup -q
%patch0 -p1 -b .config
cp %{SOURCE1} README.Mandriva

autoreconf -i

%build
%configure	--bindir=/bin \
		--sbindir=/sbin \
		--libdir=/%{_lib}
%make

%install
rm -rf %{buildroot}
%makeinstall_std

mkdir -p %{buildroot}%{_initrddir}
mv %{buildroot}%{_sysconfdir}/init.d/* %{buildroot}%{_initrddir}

# install config files
install -m644 samples/cgred.conf -D %{buildroot}%{_sysconfdir}/sysconfig/cgred.conf
install -m644 samples/cgconfig.conf -D %{buildroot}%{_sysconfdir}/cgconfig.conf
install -m644 samples/cgrules.conf -D %{buildroot}%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
mkdir -p %{buildroot}/%{_lib}/security
mv -f %{buildroot}/%{_lib}/pam_cgroup.so.*.*.* %{buildroot}/%{_lib}/security/pam_cgroup.so
rm -f %{buildroot}/%{_lib}/pam_cgroup*

# move the devel stuff to /usr
mkdir -p %{buildroot}%{_libdir}
mv -f %{buildroot}/%{_lib}/libcgroup.la %{buildroot}%{_libdir}
rm -f %{buildroot}/%{_lib}/libcgroup.so
ln -sf ../../%{_lib}/libcgroup.so.%{major} %{buildroot}%{_libdir}/libcgroup.so

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
/bin/lscgroup
/bin/lssubsys
/sbin/cgclear
/sbin/cgconfigparser
/sbin/cgrulesengd

%files pam
%defattr(-,root,root)
/%{_lib}/security/pam_cgroup.so

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/lib%{mname}.so.%{major}
/%{_lib}/lib%{mname}.so.%{major}.%{version}

%files -n %{devname}
%defattr(-,root,root)
%{_includedir}/libcgroup.h
%{_libdir}/lib%{mname}.so
%{_libdir}/lib%{mname}.la

