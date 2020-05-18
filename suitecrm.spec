Name:		suitecrm
Version:	7.11.13
Release:	1%{?dist}
Summary:	SuiteCRM Customer Relationship Management
License:	Affero GPLv3
URL:		https://suitecrm.com/
Source0:	https://suitecrm.com/files/162/SuiteCRM-7.11/500/SuiteCRM-%{version}.zip
Source1:	%{name}-sysusers.conf
Source2:	%{name}-setup
Source3:	%{name}@.service
Source4:	%{name}-scheduler@.service
Source5:	%{name}-scheduler@.timer
Source6:	%{name}-httpd.conf
Source7:	%{name}-default-httpd.conf
Source8:	%{name}-logrotate
Source9:	README.md
Patch1:		0001-rpm-Kill-the-make_writable-function.patch
Patch2:		0002-rpm-Bypass-writability-checks-for-config.php-and-con.patch
Patch3:		0003-rpm-Store-OAuth2-encryption-key-in-a-data-file-rathe.patch
BuildArch:	noarch
BuildRequires:	findutils
BuildRequires:	sed
BuildRequires:	systemd
Requires:	httpd-filesystem
Requires:	nginx-filesystem
Requires:	logrotate
Requires:	phpturd
Requires:	php-cli
Requires:	php-curl
Requires:	php-fpm
Requires:	php-gd
Requires:	php-imap
Requires:	php-json
Requires:	php-mysqlnd
Requires:	php-pcre
Requires:	php-xml
Requires:	php-zip
Requires:	php-zlib

%description
SuiteCRM is an open source Customer Relationship Management (CRM)
application written in PHP.

%prep
%autosetup -n SuiteCRM-%{version} -p 1

%build

# SuiteCRM includes an ELF executable committed to the source tree.
# Kill it with fire.
#
rm -f include/SuiteGraphs/rgraph/scripts/jsmin

# The SuiteCRM distribution zipfile includes a cache directory.  It is
# not empty.  Justified rage fills my soul.  Let the bloodshed
# commence.
#
rm -rf cache upload

# Fix file permissions
#
find . -type f -exec chmod a-x \{\} \;
chmod -R g-w,o-w .

# Add RPM readme
#
cp %{SOURCE9} README-RPM.md

%install

# Install SuiteCRM files
#
mkdir -p %{buildroot}%{_datadir}/%{name}/code
cp -a * %{buildroot}%{_datadir}/%{name}/code/

# Remove unwanted SuiteCRM files
#
rm %{buildroot}%{_datadir}/%{name}/code/*.json
rm %{buildroot}%{_datadir}/%{name}/code/*.lock
rm %{buildroot}%{_datadir}/%{name}/code/*.md
rm %{buildroot}%{_datadir}/%{name}/code/*.md5
rm %{buildroot}%{_datadir}/%{name}/code/*.xml

# Install package files
#
install -D -m 644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 755 %{SOURCE2} %{buildroot}%{_libexecdir}/%{name}-setup
install -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}@.service
install -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}-scheduler@.service
install -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/%{name}-scheduler@.timer
install -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/httpd/conf.d/50-%{name}.conf
install -D -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}-default.conf
install -D -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Create systemd placeholder directories
#
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

# Create systemd default units
#
for unit in %{name}@.service \
	    %{name}-scheduler@.service \
	    %{name}-scheduler@.timer ; do
    sed "s/%i/default/" %{buildroot}/%{_unitdir}/${unit} > \
	%{buildroot}/%{_unitdir}/${unit/@/}
done

# Mark permitted entry points
#
for file in index.php install.php \
	    service/*/rest.php service/*/soap.php \
	    themes/SuiteP/css/colourSelector.php \
	    include/social/get_feed_data.php ; do
    ln -s $(basename ${file}) \
       %{buildroot}%{_datadir}/%{name}/code/${file}.entrypoint
done

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%systemd_post %{name}.service
%systemd_post %{name}-scheduler.service
%systemd_post %{name}-scheduler.timer

%preun
%systemd_preun %{name}-scheduler.timer
%systemd_preun %{name}-scheduler.service
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service
%systemd_postun_with_restart %{name}-scheduler.service
%systemd_postun_with_restart %{name}-scheduler.timer

%files
%doc README.md
%doc README-RPM.md
%license LICENSE.txt
%dir %attr(0750, root, %{name}) %{_sysconfdir}/%{name}
%dir %attr(0750, root, %{name}) %{_sharedstatedir}/%{name}
%dir %attr(0750, root, %{name}) %{_localstatedir}/cache/%{name}
%dir %attr(0750, root, %{name}) %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/50-%{name}.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-default.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sysusersdir}/%{name}.conf
%{_libexecdir}/%{name}-setup
%{_unitdir}/%{name}@.service
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-scheduler@.service
%{_unitdir}/%{name}-scheduler.service
%{_unitdir}/%{name}-scheduler@.timer
%{_unitdir}/%{name}-scheduler.timer
%{_datadir}/%{name}/code

%changelog
