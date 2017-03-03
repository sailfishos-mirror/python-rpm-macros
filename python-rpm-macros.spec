Name:           python-rpm-macros
Version:        3
Release:        20%{?dist}
Summary:        The unversioned Python RPM macros

License:        MIT
Source0:        macros.python
Source1:        macros.python-srpm
Source2:        macros.python2
Source3:        macros.python3

BuildArch:      noarch
# For %%python3_pkgversion used in %%python_provide
Requires:       python-srpm-macros
Obsoletes:      python-macros < 3
Provides:       python-macros = %{version}-%{release}

%description
This package contains the unversioned Python RPM macros, that most
implementations should rely on.

You should not need to install this package manually as the various
python?-devel packages require it. So install a python-devel package instead.

%package -n python-srpm-macros
Summary:        RPM macros for building Python source packages

%description -n python-srpm-macros
RPM macros for building Python source packages.

%package -n python2-rpm-macros
Summary:        RPM macros for building Python 2 packages
# Would need to be different for each release - worth it?
#Conflicts:      python2-devel < 2.7.11-3

%description -n python2-rpm-macros
RPM macros for building Python 2 packages.

%package -n python3-rpm-macros
Summary:        RPM macros for building Python 3 packages
# Would need to be different for each release - worth it?
#Conflicts:      python3-devel < 3.5.1-3

%description -n python3-rpm-macros
RPM macros for building Python 3 packages.


%prep

%build

%install
mkdir -p %{buildroot}/%{rpmmacrodir}
install -m 644 %{SOURCE0} %{SOURCE1} %{SOURCE2} %{SOURCE3} \
  %{buildroot}/%{rpmmacrodir}/


%files
%{rpmmacrodir}/macros.python

%files -n python-srpm-macros
%{rpmmacrodir}/macros.python-srpm

%files -n python2-rpm-macros
%{rpmmacrodir}/macros.python2

%files -n python3-rpm-macros
%{rpmmacrodir}/macros.python3


%changelog
* Fri Mar 03 2017 Michal Cyprian <mcyprian@redhat.com> - 3-20
- Revert "Switch %%__python3 to /usr/libexec/system-python"
  after the Fedora Change https://fedoraproject.org/wiki/Changes/Making_sudo_pip_safe
  was postponed

* Fri Feb 17 2017 Michal Cyprian <mcyprian@redhat.com> - 3-19
- Switch %%__python3 to /usr/libexec/system-python

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 23 2017 Michal Cyprian <mcyprian@redhat.com> - 3-17
- Add --no-deps option to py_install_wheel macros

* Tue Jan 17 2017 Tomas Orsava <torsava@redhat.com> - 3-16
- Added macros for Build/Requires tags using Python dist tags:
  https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Nov 24 2016 Orion Poplawski <orion@cora.nwra.com> 3-15
- Make expanded macros start on the same line as the macro

* Wed Nov 16 2016 Orion Poplawski <orion@cora.nwra.com> 3-14
- Fix %%py3_install_wheel (bug #1395953)

* Wed Nov 16 2016 Orion Poplawski <orion@cora.nwra.com> 3-13
- Add missing sleeps to other build macros
- Fix build_egg macros
- Add %%py_build_wheel and %%py_install_wheel macros

* Tue Nov 15 2016 Orion Poplawski <orion@cora.nwra.com> 3-12
- Add %%py_build_egg and %%py_install_egg macros
- Allow multiple args to %%py_build/install macros
- Tidy up macro formatting

* Wed Aug 24 2016 Orion Poplawski <orion@cora.nwra.com> 3-11
- Use %%rpmmacrodir

* Tue Jul 12 2016 Orion Poplawski <orion@cora.nwra.com> 3-10
- Do not generate useless Obsoletes with %%{?_isa}

* Fri May 13 2016 Orion Poplawski <orion@cora.nwra.com> 3-9
- Make python-rpm-macros require python-srpm-macros (bug #1335860)

* Thu May 12 2016 Jason L Tibbitts III <tibbs@math.uh.edu> - 3-8
- Add single-second sleeps to work around setuptools bug.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Orion Poplawski <orion@cora.nwra.com> 3-6
- Fix typo in %%python_provide

* Thu Jan 14 2016 Orion Poplawski <orion@cora.nwra.com> 3-5
- Handle noarch python sub-packages (bug #1290900)

* Wed Jan 13 2016 Orion Poplawski <orion@cora.nwra.com> 3-4
- Fix python2/3-rpm-macros package names

* Thu Jan 7 2016 Orion Poplawski <orion@cora.nwra.com> 3-3
- Add empty %%prep and %%build

* Mon Jan 4 2016 Orion Poplawski <orion@cora.nwra.com> 3-2
- Combined package

* Wed Dec 30 2015 Orion Poplawski <orion@cora.nwra.com> 3-1
- Initial package
