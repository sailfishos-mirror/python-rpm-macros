%global basedir /opt/test/byte_compilation

Name:           pythontest
Version:        0
Release:        0
Summary:        ...
License:        MIT
BuildRequires:  python3-devel

%description
...

%install
mkdir -p %{buildroot}%{basedir}/directory/to/test/recursion

echo "print()" > %{buildroot}%{basedir}/file.py
echo "print()" > %{buildroot}%{basedir}/directory/to/test/recursion/file_in_dir.py

%py_byte_compile %{python3} %{buildroot}%{basedir}/file.py
%py_byte_compile %{python3} %{buildroot}%{basedir}/directory

%check
# Count .py and .pyc files
PY=$(find %{buildroot}%{basedir} -name "*.py" | wc -l)
PYC=$(find %{buildroot}%{basedir} -name "*.pyc" | wc -l)

# Every .py file should be byte-compiled to two .pyc files (optimization level 0 and 1)
# so we should have two times more .pyc files than .py files
test $(expr $PY \* 2) -eq $PYC

%files
%pycached %{basedir}/file.py
%pycached %{basedir}/directory/to/test/recursion/file_in_dir.py
