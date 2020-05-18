import subprocess
import sys

X_Y = f'{sys.version_info[0]}.{sys.version_info[1]}'


def rpm_eval(expression, **kwargs):
    cmd = ['rpmbuild']
    for var, value in kwargs.items():
        if value is None:
            cmd += ['--undefine', var]
        else:
            cmd += ['--define', f'{var} {value}']
    cmd += ['--eval', expression]
    cp = subprocess.run(cmd, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert cp.returncode == 0, cp.stderr
    return cp.stdout.strip().splitlines()


def test_python_provide_python():
    assert rpm_eval('%python_provide python-foo') == []


def test_python_provide_python3():
    lines = rpm_eval('%python_provide python3-foo', version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 6-1.fc66' in lines
    assert len(lines) == 3


def test_python_provide_python3_epoched():
    lines = rpm_eval('%python_provide python3-foo', epoch='1', version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 1:6-1.fc66' in lines
    assert len(lines) == 3


def test_python_provide_python3X():
    lines = rpm_eval(f'%python_provide python{X_Y}-foo', version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert 'Provides: python3-foo = 6-1.fc66' in lines
    assert len(lines) == 3


def test_python_provide_python3X_epoched():
    lines = rpm_eval(f'%python_provide python{X_Y}-foo', epoch='1', version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert 'Provides: python3-foo = 1:6-1.fc66' in lines
    assert len(lines) == 3


def test_python_provide_doubleuse():
    lines = rpm_eval('%{python_provide python3-foo}%{python_provide python3-foo}',
                     version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 6-1.fc66' in lines
    assert len(lines) == 6
    assert len(set(lines)) == 3


def test_py_provides_python():
    lines = rpm_eval('%py_provides python-foo', version='6', release='1.fc66')
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert len(lines) == 1


def test_py_provides_whatever():
    lines = rpm_eval('%py_provides whatever', version='6', release='1.fc66')
    assert 'Provides: whatever = 6-1.fc66' in lines
    assert len(lines) == 1


def test_py_provides_python3():
    lines = rpm_eval('%py_provides python3-foo', version='6', release='1.fc66')
    assert 'Provides: python3-foo = 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 6-1.fc66' in lines
    assert len(lines) == 3


def test_py_provides_python3_epoched():
    lines = rpm_eval('%py_provides python3-foo', epoch='1', version='6', release='1.fc66')
    assert 'Provides: python3-foo = 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 1:6-1.fc66' in lines
    assert len(lines) == 3


def test_py_provides_python3X():
    lines = rpm_eval(f'%py_provides python{X_Y}-foo', version='6', release='1.fc66')
    assert f'Provides: python{X_Y}-foo = 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert 'Provides: python3-foo = 6-1.fc66' in lines
    assert len(lines) == 3


def test_py_provides_python3X_epoched():
    lines = rpm_eval(f'%py_provides python{X_Y}-foo', epoch='1', version='6', release='1.fc66')
    assert f'Provides: python{X_Y}-foo = 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert 'Provides: python3-foo = 1:6-1.fc66' in lines
    assert len(lines) == 3


def test_py_provides_doubleuse():
    lines = rpm_eval('%{py_provides python3-foo}%{py_provides python3-foo}',
                     version='6', release='1.fc66')
    assert 'Provides: python3-foo = 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert f'Provides: python{X_Y}-foo = 6-1.fc66' in lines
    assert len(lines) == 6
    assert len(set(lines)) == 3


def test_py_provides_with_evr():
    lines = rpm_eval('%py_provides python3-foo 123',
                     version='6', release='1.fc66')
    assert 'Provides: python3-foo = 123' in lines
    assert 'Provides: python-foo = 123' in lines
    assert f'Provides: python{X_Y}-foo = 123' in lines
    assert len(lines) == 3


def test_pytest_passes_options_naturally():
    lines = rpm_eval('%pytest -k foo')
    assert '/usr/bin/pytest -k foo' in lines[-1]


def test_pytest_different_command():
    lines = rpm_eval('%pytest', __pytest='pytest-3')
    assert 'pytest-3' in lines[-1]


def test_pypi_source_default_name():
    url = rpm_eval('%pypi_source',
                   name='foo', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz'


def test_pypi_source_default_srcname():
    url = rpm_eval('%pypi_source',
                   name='python-foo', srcname='foo', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz'


def test_pypi_source_default_pypi_name():
    url = rpm_eval('%pypi_source',
                   name='python-foo', pypi_name='foo', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz'


def test_pypi_source_default_name_uppercase():
    url = rpm_eval('%pypi_source',
                   name='Foo', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/F/Foo/Foo-6.tar.gz'


def test_pypi_source_provided_name():
    url = rpm_eval('%pypi_source foo',
                   name='python-bar', pypi_name='bar', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz'


def test_pypi_source_provided_name_version():
    url = rpm_eval('%pypi_source foo 6',
                   name='python-bar', pypi_name='bar', version='3')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz'


def test_pypi_source_provided_name_version_ext():
    url = rpm_eval('%pypi_source foo 6 zip',
                   name='python-bar', pypi_name='bar', version='3')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6.zip'


def test_pypi_source_prerelease():
    url = rpm_eval('%pypi_source',
                   name='python-foo', pypi_name='foo', version='6~b2')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6b2.tar.gz'


def test_pypi_source_explicit_tilde():
    url = rpm_eval('%pypi_source foo 6~6',
                   name='python-foo', pypi_name='foo', version='6')[0]
    assert url == 'https://files.pythonhosted.org/packages/source/f/foo/foo-6~6.tar.gz'


def test_py3_shebang_fix():
    cmd = rpm_eval('%py3_shebang_fix arg1 arg2 arg3')[0]
    assert cmd == '/usr/bin/pathfix.py -pni /usr/bin/python3 -ka s arg1 arg2 arg3'


def test_py3_shebang_fix_custom_flags():
    cmd = rpm_eval('%py3_shebang_fix arg1 arg2 arg3', py3_shebang_flags='Es')[0]
    assert cmd == '/usr/bin/pathfix.py -pni /usr/bin/python3 -ka Es arg1 arg2 arg3'


def test_py3_shebang_fix_empty_flags():
    cmd = rpm_eval('%py3_shebang_fix arg1 arg2 arg3', py3_shebang_flags=None)[0]
    assert cmd == '/usr/bin/pathfix.py -pni /usr/bin/python3 -k arg1 arg2 arg3'


def test_py_shebang_fix_custom():
    cmd = rpm_eval('%py_shebang_fix arg1 arg2 arg3', __python='/usr/bin/pypy')[0]
    assert cmd == '/usr/bin/pathfix.py -pni /usr/bin/pypy -ka s arg1 arg2 arg3'
