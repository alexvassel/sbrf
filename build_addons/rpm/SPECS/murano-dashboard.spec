Name:          murano-dashboard
Version:       0.5
Release:       2%{?dist}
Summary:       OpenStack Murano Dashboard
Group:         Applications/Communications
License:       Apache License, Version 2.0
URL:           https://launchpad.net/murano
Source0:       murano-dashboard-0.5.tar.gz
Source1:       modify-horizon-config.sh
BuildArch:     noarch
Requires:      openstack-dashboard
Requires:      python-eventlet
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr
BuildRequires: python-d2to1
# Murano direct dependencies:
Requires:      python-anyjson >= 0.3.3
Requires:      python-iso8601 >= 0.1.9
Requires:      python-pbr >= 0.6, python-pbr < 0.7, python-pbr > 0.7, python-pbr < 1.0
Requires:      PyYAML >= 3.1.0
Requires:      python-six >= 1.7.0
# Incompatible with global requirements:
Requires:      python-django-floppyforms >= 1.1
Requires:      python-muranoclient >= 0.5.5
Requires:      python-yaql >= 0.2.3, python-yaql < 0.3


%description
Murano Dashboard
Sytem package - murano-dashboard
Python package - murano-dashboard

%prep
%setup -q muranodashboard-%{version}

%build
%{__python} setup.py build

%install
mkdir -p %{buildroot}/var/cache/muranodashboard-cache

%{__python} setup.py install -O1 --skip-build --root %{buildroot}
mkdir -p  %{buildroot}/usr/bin
#cp %{_builddir}/murano-dashboard-%{version}/build_addons/rpm/modify-horizon-config.sh %{buildroot}/usr/bin/
cp %SOURCE1 %{buildroot}/usr/bin/


%post
# Save all symbolic links from openstack_dashboard/static dir
CURRENT_DIR=$(pwd)
os_dashboard_static_dir=/usr/share/openstack-dashboard/static
cd $os_dashboard_static_dir
rm -f .symlinks
for f in $(find . -type l); do
    printf "Saving symlink '%s' ...\n" $f
    printf "%s\t%s\n" $f $(readlink $f) >> .symlinks
    rm -f $f
done
cd $CURRENT_DIR
#------------------------
chmod a+x /usr/bin/modify-horizon-config.sh
USE_SQLITE_BACKEND=False
MURANO_DASHBOARD_CACHE=/var/cache/muranodashboard-cache
MURANO_DASHBOARD_CACHE=$MURANO_DASHBOARD_CACHE USE_SQLITE_BACKEND=$USE_SQLITE_BACKEND /usr/bin/modify-horizon-config.sh install

mkdir -p /usr/share/openstack-dashboard/static/floppyforms
mkdir -p /usr/share/openstack-dashboard/static/muranodashboard
chown -R apache:root /usr/share/openstack-dashboard/static/muranodashboard
chown -R apache:root /usr/share/openstack-dashboard/static/floppyforms

su -c "python /usr/share/openstack-dashboard/manage.py collectstatic --noinput | /usr/bin/logger -t murano-dashboard-install " -s /bin/bash apache

# Restore sympbolic links
cd $os_dashboard_static_dir
if [ ! -f .symlinks ]; then
    cd $currdir
fi
while read name path; do
    printf "Restoring symlink '%s' ...\n" $f
        if [ -d "$name" ]; then
            rm -rf "$name"
        fi
        ln -s "$path" "$name"
done < .symlinks
rm -f .symlinks
cd $CURRENT_DIR
#------------------------
if [ "$USE_SQLITE_BACKEND" == "True" ]; then
    su -c "python /usr/share/openstack-dashboard/manage.py syncdb --noinput | /usr/bin/logger -t murano-dashboard-install " -s /bin/bash apache
fi
service httpd restart

%preun
/usr/bin/modify-horizon-config.sh uninstall
service httpd restart

%clean
rm -rf %{buildroot}

%files
%{python_sitelib}/*
/usr/bin/*
%dir %attr(755, apache, apache) /var/cache/muranodashboard-cache

%changelog
* Wed Jul 1 2014 Igor Yozhikov <iyozhikov@mirantis.com>
- updated for LP BP

* Tue Jun 24 2014 built by Igor Yozhikov <iyozhikov@mirantis.com>
- requirements update for MOS 5.0.1 build

* Mon Apr 10 2014 built by Igor Yozhikov <iyozhikov@mirantis.com>
- build number - 2 for rel 0.5 with updated requirements and changed postinstall section

* Mon Feb 25 2014 built by Igor Yozhikov <iyozhikov@mirantis.com>
- build number - 1 for rel 0.4.1 with new spec

* Fri Dec 13 2013 built by Igor Yozhikov <iyozhikov@mirantis.com>
- build number - 5
