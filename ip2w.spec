License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Summary:  A daemon which gets weather by IP


%description
A daemon which gets weather by IP
Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /var/log
%define __bindir    /usr/local/%{name}
%define __systemddir	/usr/lib/systemd/system
%define __appsource 	/home/%{name}

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__mkdir} -p %{buildroot}/%{__etcdir}/%{name}
%{__mkdir} -p %{buildroot}%{__logdir}/%{name}

%{__install} -pD -m 644 %{__appsource}/%{name}.service %{buildroot}/%{__systemddir}/%{name}.service
%{__install} -m 755 %{__appsource}/%{name}.py %{buildroot}/%{__bindir}
%{__install} -m 755 %{__appsource}/%{name}_config.json %{buildroot}/%{__etcdir}/%{name}
%{__install} -m 755 %{__appsource}/uwsgi.ini %{buildroot}/%{__etcdir}/%{name}
touch %{buildroot}%{__logdir}/%{name}/%{name}.log

%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}/%{name}
%{__bindir}
%{__systemddir}
%{__etcdir}/%{name}
