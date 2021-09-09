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

# Files in sitelib are compiled automatically by brp-python-bytecompile
mkdir -p %{buildroot}%{python3_sitelib}/directory/
echo "print()" > %{buildroot}%{python3_sitelib}/directory/file.py

%check
LOCATIONS="%{buildroot}%{basedir} %{buildroot}%{python3_sitelib}/directory/"

# Count .py and .pyc files
PY=$(find $LOCATIONS -name "*.py" | wc -l)
PYC=$(find $LOCATIONS -name "*.pyc" | wc -l)

# We should have 3 .py files
test $PY -eq 3

# Every .py file should be byte-compiled to two .pyc files (optimization level 0 and 1)
# so we should have two times more .pyc files than .py files
test $(expr $PY \* 2) -eq $PYC

# In this case the .pyc files should be identical across omtimization levels
# (they don't use docstrings and assert staements)
# So they should be hardlinked; the number of distinct inodes should match the
# number of source files. (Or be smaller, if the dupe detection is done
# across all files.)

INODES=$(stat --format %i $(find $LOCATIONS -name "*.pyc") | sort -u | wc -l)
test $PY -ge $INODES


%files
%pycached %{basedir}/file.py
%pycached %{basedir}/directory/to/test/recursion/file_in_dir.py
%pycached %{python3_sitelib}/directory/file.py
