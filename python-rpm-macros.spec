Name:           python-rpm-macros
Summary:        The common Python RPM macros

# Macros:
Source101:      macros.python
Source102:      macros.python-srpm
Source104:      macros.python3
Source105:      macros.pybytecompile

# Lua files
Source201:      python.lua

# Python code
%global compileall2_version 0.7.1
Source301:      https://github.com/fedora-python/compileall2/raw/v%{compileall2_version}/compileall2.py

# macros and lua: MIT, compileall2.py: PSFv2
License:        MIT and Python

# The package version MUST be always the same as %%{__default_python3_version}.
# To have only one source of truth, we load the macro and use it.
# The macro is defined in python-srpm-macros.
                %{load:%{SOURCE102}}
Version:        %{__default_python3_version}
Release:        35%{?dist}

BuildArch:      noarch

# For %%__default_python3_pkgversion used in %%python_provide
# For python.lua
# For compileall2.py
Requires:       python-srpm-macros = %{version}-%{release}

%description
This package contains the unversioned Python RPM macros, that most
implementations should rely on.

You should not need to install this package manually as the various
python?-devel packages require it. So install a python-devel package instead.


%package -n python-srpm-macros
Summary:        RPM macros for building Python source packages

# For directory structure and flags macros
Requires:       redhat-rpm-config

# We bundle our own software here :/
Provides:       bundled(python3dist(compileall2)) = %{compileall2_version}

%description -n python-srpm-macros
RPM macros for building Python source packages.


%package -n python3-rpm-macros
Summary:        RPM macros for building Python 3 packages

# For %%__python3 and %%python3
Requires:       python-srpm-macros = %{version}-%{release}

# For %%py_setup
Requires:       python-rpm-macros = %{version}-%{release}

%description -n python3-rpm-macros
RPM macros for building Python 3 packages.


%prep
%autosetup -c -T
cp -a %{sources} .


%install
mkdir -p %{buildroot}%{rpmmacrodir}
install -m 644 macros.* %{buildroot}%{rpmmacrodir}/

mkdir -p %{buildroot}%{_rpmluadir}/fedora/srpm
install -p -m 644 -t %{buildroot}%{_rpmluadir}/fedora/srpm python.lua

mkdir -p %{buildroot}%{_rpmconfigdir}/redhat
install -m 644 compileall2.py %{buildroot}%{_rpmconfigdir}/redhat/


%files
%{rpmmacrodir}/macros.python
%{rpmmacrodir}/macros.pybytecompile

%files -n python-srpm-macros
%{rpmmacrodir}/macros.python-srpm
%{_rpmconfigdir}/redhat/compileall2.py
%{_rpmluadir}/fedora/srpm/python.lua

%files -n python3-rpm-macros
%{rpmmacrodir}/macros.python3


%changelog
* Sat Feb 20 2021 Miro Hrončok <mhroncok@redhat.com> - 3.9-35
- Fix %%python_extras_subpkg with underscores in extras names

* Mon Feb 08 2021 Miro Hrončok <mhroncok@redhat.com> - 3.9-34
- Remove python2-rpm-macros
- https://fedoraproject.org/wiki/Changes/Disable_Python_2_Dist_RPM_Generators_and_Freeze_Python_2_Macros

* Fri Feb 05 2021 Miro Hrončok <mhroncok@redhat.com> - 3.9-13
- Automatically word-wrap the description of extras subpackages
- Fixes: rhbz#1922442

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.9-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Dec 08 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-11
- Support defining %%py3_shebang_flags to %%nil

* Mon Sep 14 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-10
- Add %%python3_platform_triplet and %%python3_ext_suffix
- https://fedoraproject.org/wiki/Changes/Python_Upstream_Architecture_Names

* Fri Jul 24 2020 Lumír Balhar <lbalhar@redhat.com> - 3.9-9
- Adapt %%py[3]_shebang_fix to use versioned pathfixX.Y.py

* Fri Jul 24 2020 Lumír Balhar <lbalhar@redhat.com> - 3.9-8
- Disable Python hash seed randomization in %%py_byte_compile

* Tue Jul 21 2020 Lumír Balhar <lbalhar@redhat.com> - 3.9-7
- Make %%py3_dist respect %%python3_pkgversion

* Thu Jul 16 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-6
- Make the unversioned %%__python macro error
- https://fedoraproject.org/wiki/Changes/PythonMacroError
- Make %%python macros more consistent with %%python3 macros
- Define %%python_platform (as a Python version agnostic option to %%python3_platform)
- Add --no-index --no-warn-script-location pip options to %%pyX_install_wheel

* Wed Jul 08 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-5
- Introduce %%python_extras_subpkg
- Adapt %%py_dist_name to keep square brackets
- https://fedoraproject.org/wiki/Changes/PythonExtras

* Tue Jun 16 2020 Lumír Balhar <lbalhar@redhat.com> - 3.9-4
- Use compileall from stdlib for Python >= 3.9

* Thu Jun 11 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-3
- Allow to combine %%pycached with other macros (e.g. %%exclude or %%ghost) (#1838992)

* Sat May 30 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-2
- Require the exact same version-release of other subpackages of this package

* Thu May 21 2020 Miro Hrončok <mhroncok@redhat.com> - 3.9-1
- https://fedoraproject.org/wiki/Changes/Python3.9
- Switch the %%py_dist_name macro to convert dots (".") into dashes as defined in PEP 503 (#1791530)

* Mon May 11 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-8
- Implement %%pytest
- Implement %%pyX_shebang_fix
- Strip tildes from %%version in %%pypi_source by default

* Thu May 07 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-7
- Change %%__default_python3_pkgversion from 38 to 3.8

* Tue May 05 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-6
- Require recent enough SRPM macros from RPM macros, to prevent missing Lua files

* Tue May 05 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-5
- Implement %%py_provides

* Mon May 04 2020 Tomas Hrnciar <thrnciar@redhat.com> - 3.8-4
- Make %%py3_install_wheel macro remove direct_url.json file created by PEP 610.
- https://discuss.python.org/t/pep-610-usage-guidelines-for-linux-distributions/4012

* Mon Apr 27 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-3
- Make pythonX-rpm-macros depend on python-rpm-macros (#1827811)

* Tue Mar 31 2020 Lumír Balhar <lbalhar@redhat.com> - 3.8-2
- Update of bundled compileall2 module to 0.7.1 (bugfix release)

* Mon Mar 23 2020 Miro Hrončok <mhroncok@redhat.com> - 3.8-1
- Hardcode the default Python 3 version in the SRPM macros (#1812087)
- Provide python38-foo for python3-foo and the other way around (future RHEL compatibility)
- %%python_provide: Allow any names starting with "python" or "pypy"

* Mon Feb 10 2020 Miro Hrončok <mhroncok@redhat.com> - 3-54
- Update of bundled compileall2 module to 0.7.0
  Adds the optional --hardlink-dupes flag for compileall2 for pyc deduplication

* Thu Feb 06 2020 Miro Hrončok <mhroncok@redhat.com> - 3-53
- Define %%py(2|3)?_shbang_opts_nodash to be used with pathfix.py -a

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3-52
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Dec 28 2019 Miro Hrončok <mhroncok@redhat.com> - 3-51
- Define %%python, but make it work only if %%__python is redefined
- Add the %%pycached macro
- Remove stray __pycache__ directory from /usr/bin when running %%py_install,
  %%py_install_wheel and %%py_build_wheel macros

* Tue Nov 26 2019 Lumír Balhar <lbalhar@redhat.com> - 3-50
- Update of bundled compileall2 module

* Fri Sep 27 2019 Miro Hrončok <mhroncok@redhat.com> - 3-49
- Define %%python2 and %%python3

* Mon Aug 26 2019 Miro Hrončok <mhroncok@redhat.com> - 3-48
- Drop --strip-file-prefix option from %%pyX_install_wheel macros, it is not needed

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3-47
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 12 2019 Miro Hrončok <mhroncok@redhat.com> - 3-46
- %%python_provide: Switch python2 and python3 behavior
- https://fedoraproject.org/wiki/Changes/Python_means_Python3
- Use compileall2 module for byte-compilation with Python >= 3.4
- Do not allow passing arguments to Python during byte-compilation
- Use `-s` argument for Python during byte-compilation

* Tue Jul 09 2019 Miro Hrončok <mhroncok@redhat.com> - 3-45
- %%python_provide: Don't try to obsolete %%_isa provides

* Mon Jun 17 2019 Miro Hrončok <mhroncok@redhat.com> - 3-44
- Make %%__python /usr/bin/python once again until we are ready

* Mon Jun 10 2019 Miro Hrončok <mhroncok@redhat.com> - 3-43
- Define %%python_sitelib, %%python_sitearch, %%python_version, %%python_version_nodots,
  in rpm 4.15 those are no longer defined, the meaning of python is derived from %%__python.
- Usage of %%__python or the above-mentioned macros will error unless user defined.
- The %%python_provide macro no longer gives the arched provide for arched packages (#1705656)

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3-42
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Dec 20 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3-41
- Add %%python_disable_dependency_generator

* Wed Dec 05 2018 Miro Hrončok <mhroncok@redhat.com> - 3-40
- Workaround leaking buildroot PATH in %py_byte_compile (#1647212)

* Thu Nov 01 2018 Petr Viktorin <pviktori@redhat.com> - 3-39
- Move "sleep 1" workaround from py3_build to py2_build (#1644923)

* Thu Sep 20 2018 Tomas Orsava <torsava@redhat.com> - 3-38
- Move the __python2/3 macros to the python-srpm-macros subpackage
- This facilitates using the %%{__python2/3} in Build/Requires

* Wed Aug 15 2018 Miro Hrončok <mhroncok@redhat.com> - 3-37
- Make %%py_byte_compile terminate build on SyntaxErrors (#1616219)

* Wed Aug 15 2018 Miro Hrončok <mhroncok@redhat.com> - 3-36
- Make %%py_build wokr if %%__python is defined to custom value

* Sat Jul 28 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3-35
- Change way how enabling-depgen works internally

* Sat Jul 14 2018 Tomas Orsava <torsava@redhat.com> - 3-34
- macros.pybytecompile: Detect Python version through sys.version_info instead
  of guessing from the executable name

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3-33
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 10 2018 Tomas Orsava <torsava@redhat.com> - 3-32
- Fix %%py_byte_compile macro: when invoked with a Python 2 binary it also
  mistakenly ran py3_byte_compile

* Tue Jul 03 2018 Miro Hrončok <mhroncok@redhat.com> - 3-31
- Add %%python3_platform useful for PYTHONPATH on arched builds

* Mon Jun 18 2018 Jason L Tibbitts III <tibbs@math.uh.edu> - 3-30
- Add %%pypi_source macro, as well as %%__pypi_url and
  %%_pypi_default_extension.

* Wed Apr 18 2018 Miro Hrončok <mhroncok@redhat.com> - 3-29
- move macros.pybytecompile from python3-devel

* Fri Apr 06 2018 Tomas Orsava <torsava@redhat.com> - 3-28
- Fix the %%py_dist_name macro to not convert dots (".") into dashes, so that
  submodules can be addressed as well
Resolves: rhbz#1564095

* Fri Mar 23 2018 Miro Hrončok <mhroncok@redhat.com> - 3-27
- make LDFLAGS propagated whenever CFLAGS are

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 19 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3-25
- Add %%python_enable_dependency_generator

* Tue Nov 28 2017 Tomas Orsava <torsava@redhat.com> - 3-24
- Remove platform-python macros (https://fedoraproject.org/wiki/Changes/Platform_Python_Stack)

* Thu Oct 26 2017 Ville Skyttä <ville.skytta@iki.fi> - 3-23
- Use -Es/-I to invoke macro scriptlets (#1506355)

* Wed Aug 02 2017 Tomas Orsava <torsava@redhat.com> - 3-22
- Add platform-python macros (https://fedoraproject.org/wiki/Changes/Platform_Python_Stack)

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

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
