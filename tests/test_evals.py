import os
import subprocess
import platform
import re
import sys
import textwrap

import pytest

X_Y = f'{sys.version_info[0]}.{sys.version_info[1]}'
XY = f'{sys.version_info[0]}{sys.version_info[1]}'

# Handy environment variable you can use to run the tests
# with modified macros files. Multiple files should be
# separated by colon.
# You can use * if you escape it from your Shell:
# TESTED_FILES='macros.*' pytest -v
# Remember that some tests might need more macros files than just
# the local ones. You might need to use:
# TESTED_FILES='/usr/lib/rpm/macros:/usr/lib/rpm/platform/x86_64-linux/macros:macros.*'
TESTED_FILES = os.getenv("TESTED_FILES", None)


def rpm_eval(expression, fails=False, **kwargs):
    cmd = ['rpmbuild']
    if TESTED_FILES:
        cmd += ['--macros', TESTED_FILES]
    for var, value in kwargs.items():
        if value is None:
            cmd += ['--undefine', var]
        else:
            cmd += ['--define', f'{var} {value}']
    cmd += ['--eval', expression]
    cp = subprocess.run(cmd, text=True, env={**os.environ, 'LANG': 'C.utf-8'},
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if fails:
        assert cp.returncode != 0, cp.stdout
    elif fails is not None:
        assert cp.returncode == 0, cp.stdout
    return cp.stdout.strip().splitlines()


@pytest.fixture(scope="session")
def lib():
    lib_eval = rpm_eval("%_lib")[0]
    if lib_eval == "%_lib" and TESTED_FILES:
        raise ValueError(
            "%_lib is not resolved to an actual value. "
            "You may want to include /usr/lib/rpm/platform/x86_64-linux/macros to TESTED_FILES."
        )
    return lib_eval


def shell_stdout(script):
    return subprocess.check_output(script,
                                   env={**os.environ, 'LANG': 'C.utf-8'},
                                   text=True,
                                   shell=True).rstrip()


@pytest.mark.parametrize('argument, result', [
    ('a', 'a'),
    ('a-a', 'a-a'),
    ('a_a', 'a-a'),
    ('a.a', 'a-a'),
    ('a---a', 'a-a'),
    ('a-_-a', 'a-a'),
    ('a-_-a', 'a-a'),
    ('a[b]', 'a[b]'),
    ('Aha[Boom]', 'aha[boom]'),
    ('a.a[b.b]', 'a-a[b-b]'),
])
def test_pydist_name(argument, result):
    assert rpm_eval(f'%py_dist_name {argument}') == [result]


def test_py2_dist():
    assert rpm_eval(f'%py2_dist Aha[Boom] a') == ['python2dist(aha[boom]) python2dist(a)']


def test_py3_dist():
    assert rpm_eval(f'%py3_dist Aha[Boom] a') == ['python3dist(aha[boom]) python3dist(a)']


def test_py3_dist_with_python3_pkgversion_redefined():
    assert rpm_eval(f'%py3_dist Aha[Boom] a', python3_pkgversion="3.6") == ['python3.6dist(aha[boom]) python3.6dist(a)']


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


def test_python_wheel_pkg_prefix():
    assert rpm_eval('%python_wheel_pkg_prefix', fedora='44', rhel=None, eln=None) == ['python']
    assert rpm_eval('%python_wheel_pkg_prefix', fedora='44', rhel=None, eln=None, python3_pkgversion='3.9') == ['python']
    assert rpm_eval('%python_wheel_pkg_prefix', fedora=None, rhel='1', eln='1') == ['python']
    assert rpm_eval('%python_wheel_pkg_prefix', fedora=None, rhel='1', eln=None) == ['python3']
    assert rpm_eval('%python_wheel_pkg_prefix', fedora=None, rhel='1', eln=None, python3_pkgversion='3.10') == ['python3.10']
    assert rpm_eval('%python_wheel_pkg_prefix', fedora=None, rhel='1', eln=None, python3_pkgversion='3.11') == ['python3.11']


def test_python_wheel_dir():
    assert rpm_eval('%python_wheel_dir', fedora='44', rhel=None, eln=None) == ['/usr/share/python-wheels']
    assert rpm_eval('%python_wheel_dir', fedora='44', rhel=None, eln=None, python3_pkgversion='3.9') == ['/usr/share/python-wheels']
    assert rpm_eval('%python_wheel_dir', fedora=None, rhel='1', eln='1') == ['/usr/share/python-wheels']
    assert rpm_eval('%python_wheel_dir', fedora=None, rhel='1', eln=None) == ['/usr/share/python3-wheels']
    assert rpm_eval('%python_wheel_dir', fedora=None, rhel='1', eln=None, python3_pkgversion='3.10') == ['/usr/share/python3.10-wheels']
    assert rpm_eval('%python_wheel_dir', fedora=None, rhel='1', eln=None, python3_pkgversion='3.11') == ['/usr/share/python3.11-wheels']


def test_pytest_passes_options_naturally():
    lines = rpm_eval('%pytest -k foo')
    assert '/usr/bin/pytest -k foo' in lines[-1]


def test_pytest_different_command():
    lines = rpm_eval('%pytest', __pytest='pytest-3')
    assert 'pytest-3' in lines[-1]


def test_pytest_command_suffix():
    lines = rpm_eval('%pytest -v')
    assert '/usr/bin/pytest -v' in lines[-1]
    lines = rpm_eval('%pytest -v', python3_pkgversion="3.6", python3_version="3.6")
    assert '/usr/bin/pytest-3.6 -v' in lines[-1]


def test_pytest_undefined_addopts_are_not_set():
    lines = rpm_eval('%pytest', __pytest_addopts=None)
    assert 'PYTEST_ADDOPTS' not in '\n'.join(lines)


def test_pytest_defined_addopts_are_set():
    lines = rpm_eval('%pytest', __pytest_addopts="--ignore=stuff")
    assert 'PYTEST_ADDOPTS="${PYTEST_ADDOPTS:-} --ignore=stuff"' in '\n'.join(lines)


@pytest.mark.parametrize('__pytest_addopts', ['--macronized-option', 'x y z', None])
def test_pytest_addopts_preserves_envvar(__pytest_addopts):
    # this is the line a packager might put in the spec file before running %pytest:
    spec_line = 'export PYTEST_ADDOPTS="--exported-option1 --exported-option2"'

    # instead of actually running /usr/bin/pytest,
    # we run a small shell script that echoes the tested value for inspection
    lines = rpm_eval('%pytest', __pytest_addopts=__pytest_addopts,
                     __pytest="sh -c 'echo $PYTEST_ADDOPTS'")

    echoed = shell_stdout('\n'.join([spec_line] + lines))

    # assert all values were echoed
    assert '--exported-option1' in echoed
    assert '--exported-option2' in echoed
    if __pytest_addopts is not None:
        assert __pytest_addopts in echoed

    # assert the options are separated
    assert 'option--' not in echoed
    assert 'z--' not in echoed


def test_pypi_source_default_name():
    urls = rpm_eval('%pypi_source',
                    name='foo', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz']


def test_pypi_source_default_srcname():
    urls = rpm_eval('%pypi_source',
                    name='python-foo', srcname='foo', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz']


def test_pypi_source_default_pypi_name():
    urls = rpm_eval('%pypi_source',
                    name='python-foo', pypi_name='foo', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz']


def test_pypi_source_default_name_uppercase():
    urls = rpm_eval('%pypi_source',
                    name='Foo', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/F/Foo/Foo-6.tar.gz']


def test_pypi_source_provided_name():
    urls = rpm_eval('%pypi_source foo',
                    name='python-bar', pypi_name='bar', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz']


def test_pypi_source_provided_name_version():
    urls = rpm_eval('%pypi_source foo 6',
                    name='python-bar', pypi_name='bar', version='3')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.tar.gz']


def test_pypi_source_provided_name_version_ext():
    url = rpm_eval('%pypi_source foo 6 zip',
                   name='python-bar', pypi_name='bar', version='3')
    assert url == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6.zip']


def test_pypi_source_prerelease():
    urls = rpm_eval('%pypi_source',
                    name='python-foo', pypi_name='foo', version='6~b2')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6b2.tar.gz']


def test_pypi_source_explicit_tilde():
    urls = rpm_eval('%pypi_source foo 6~6',
                    name='python-foo', pypi_name='foo', version='6')
    assert urls == ['https://files.pythonhosted.org/packages/source/f/foo/foo-6~6.tar.gz']


def test_py3_shebang_fix():
    cmd = rpm_eval('%py3_shebang_fix arg1 arg2 arg3')[-1].strip()
    assert cmd == '$pathfix -pni /usr/bin/python3 $shebang_flags arg1 arg2 arg3'


def test_py3_shebang_fix_default_shebang_flags():
    lines = rpm_eval('%py3_shebang_fix arg1 arg2')
    lines[-1] = 'echo $shebang_flags'
    assert shell_stdout('\n'.join(lines)) == '-kas'


def test_py3_shebang_fix_custom_shebang_flags():
    lines = rpm_eval('%py3_shebang_fix arg1 arg2', py3_shebang_flags='Es')
    lines[-1] = 'echo $shebang_flags'
    assert shell_stdout('\n'.join(lines)) == '-kaEs'


@pytest.mark.parametrize('flags', [None, '%{nil}'])
def test_py3_shebang_fix_no_shebang_flags(flags):
    lines = rpm_eval('%py3_shebang_fix arg1 arg2', py3_shebang_flags=flags)
    lines[-1] = 'echo $shebang_flags'
    assert shell_stdout('\n'.join(lines)) == '-k'


def test_py_shebang_fix_custom_python():
    cmd = rpm_eval('%py_shebang_fix arg1 arg2 arg3', __python='/usr/bin/pypy')[-1].strip()
    assert cmd == '$pathfix -pni /usr/bin/pypy $shebang_flags arg1 arg2 arg3'


def test_pycached_in_sitelib():
    lines = rpm_eval('%pycached %{python3_sitelib}/foo*.py')
    assert lines == [
        f'/usr/lib/python{X_Y}/site-packages/foo*.py',
        f'/usr/lib/python{X_Y}/site-packages/__pycache__/foo*.cpython-{XY}{{,.opt-?}}.pyc'
    ]


def test_pycached_in_sitearch(lib):
    lines = rpm_eval('%pycached %{python3_sitearch}/foo*.py')
    assert lines == [
        f'/usr/{lib}/python{X_Y}/site-packages/foo*.py',
        f'/usr/{lib}/python{X_Y}/site-packages/__pycache__/foo*.cpython-{XY}{{,.opt-?}}.pyc'
    ]


def test_pycached_in_36():
    lines = rpm_eval('%pycached /usr/lib/python3.6/site-packages/foo*.py')
    assert lines == [
        '/usr/lib/python3.6/site-packages/foo*.py',
        '/usr/lib/python3.6/site-packages/__pycache__/foo*.cpython-36{,.opt-?}.pyc'
    ]


def test_pycached_in_custom_dir():
    lines = rpm_eval('%pycached /bar/foo*.py')
    assert lines == [
        '/bar/foo*.py',
        '/bar/__pycache__/foo*.cpython-3*{,.opt-?}.pyc'
    ]


def test_pycached_with_exclude():
    lines = rpm_eval('%pycached %exclude %{python3_sitelib}/foo*.py')
    assert lines == [
        f'%exclude /usr/lib/python{X_Y}/site-packages/foo*.py',
        f'%exclude /usr/lib/python{X_Y}/site-packages/__pycache__/foo*.cpython-{XY}{{,.opt-?}}.pyc'
    ]


def test_pycached_fails_with_extension_glob():
    lines = rpm_eval('%pycached %{python3_sitelib}/foo.py*', fails=True)
    assert lines[0] == 'error: %pycached can only be used with paths explicitly ending with .py'


def test_python_extras_subpkg_i():
    lines = rpm_eval('%python_extras_subpkg -n python3-setuptools_scm -i %{python3_sitelib}/*.egg-info toml yaml',
                     version='6', release='7')
    expected = textwrap.dedent(f"""
        %package -n python3-setuptools_scm+toml
        Summary: Metapackage for python3-setuptools_scm: toml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+toml
        This is a metapackage bringing in toml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.

        %files -n python3-setuptools_scm+toml
        %ghost /usr/lib/python{X_Y}/site-packages/*.egg-info

        %package -n python3-setuptools_scm+yaml
        Summary: Metapackage for python3-setuptools_scm: yaml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+yaml
        This is a metapackage bringing in yaml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.

        %files -n python3-setuptools_scm+yaml
        %ghost /usr/lib/python{X_Y}/site-packages/*.egg-info
        """).lstrip().splitlines()
    assert lines == expected


def test_python_extras_subpkg_f():
    lines = rpm_eval('%python_extras_subpkg -n python3-setuptools_scm -f ghost_filelist toml yaml',
                     version='6', release='7')
    expected = textwrap.dedent(f"""
        %package -n python3-setuptools_scm+toml
        Summary: Metapackage for python3-setuptools_scm: toml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+toml
        This is a metapackage bringing in toml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.

        %files -n python3-setuptools_scm+toml -f ghost_filelist

        %package -n python3-setuptools_scm+yaml
        Summary: Metapackage for python3-setuptools_scm: yaml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+yaml
        This is a metapackage bringing in yaml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.

        %files -n python3-setuptools_scm+yaml -f ghost_filelist
        """).lstrip().splitlines()
    assert lines == expected


def test_python_extras_subpkg_F():
    lines = rpm_eval('%python_extras_subpkg -n python3-setuptools_scm -F toml yaml',
                     version='6', release='7')
    expected = textwrap.dedent(f"""
        %package -n python3-setuptools_scm+toml
        Summary: Metapackage for python3-setuptools_scm: toml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+toml
        This is a metapackage bringing in toml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.



        %package -n python3-setuptools_scm+yaml
        Summary: Metapackage for python3-setuptools_scm: yaml extras
        Requires: python3-setuptools_scm = 6-7
        %description -n python3-setuptools_scm+yaml
        This is a metapackage bringing in yaml extras requires for
        python3-setuptools_scm.
        It makes sure the dependencies are installed.
        """).lstrip().splitlines()
    assert lines == expected


def test_python_extras_subpkg_underscores():
    lines = rpm_eval('%python_extras_subpkg -n python3-webscrapbook -F adhoc_ssl',
                     version='0.33.3', release='1.fc33')
    expected = textwrap.dedent(f"""
        %package -n python3-webscrapbook+adhoc_ssl
        Summary: Metapackage for python3-webscrapbook: adhoc_ssl extras
        Requires: python3-webscrapbook = 0.33.3-1.fc33
        %description -n python3-webscrapbook+adhoc_ssl
        This is a metapackage bringing in adhoc_ssl extras requires for
        python3-webscrapbook.
        It makes sure the dependencies are installed.
        """).lstrip().splitlines()
    assert lines == expected


@pytest.mark.parametrize('sep', [pytest.param(('', ' ', ' ', ''), id='spaces'),
                                 pytest.param(('', ',', ',', ''), id='commas'),
                                 pytest.param(('', ',', ',', ','), id='commas-trailing'),
                                 pytest.param((',', ',', ',', ''), id='commas-leading'),
                                 pytest.param((',', ',', ',', ','), id='commas-trailing-leading'),
                                 pytest.param(('', ',', ' ', ''), id='mixture'),
                                 pytest.param(('  ', '   ', '\t\t, ', '\t'), id='chaotic-good'),
                                 pytest.param(('', '\t ,, \t\r ', ',,\t  , ', ',,'), id='chaotic-evil')])
def test_python_extras_subpkg_arg_separators(sep):
    lines = rpm_eval('%python_extras_subpkg -n python3-hypothesis -F {}cli{}ghostwriter{}pytz{}'.format(*sep),
                     version='6.6.0', release='1.fc35')
    expected = textwrap.dedent(f"""
        %package -n python3-hypothesis+cli
        Summary: Metapackage for python3-hypothesis: cli extras
        Requires: python3-hypothesis = 6.6.0-1.fc35
        %description -n python3-hypothesis+cli
        This is a metapackage bringing in cli extras requires for python3-hypothesis.
        It makes sure the dependencies are installed.



        %package -n python3-hypothesis+ghostwriter
        Summary: Metapackage for python3-hypothesis: ghostwriter extras
        Requires: python3-hypothesis = 6.6.0-1.fc35
        %description -n python3-hypothesis+ghostwriter
        This is a metapackage bringing in ghostwriter extras requires for
        python3-hypothesis.
        It makes sure the dependencies are installed.



        %package -n python3-hypothesis+pytz
        Summary: Metapackage for python3-hypothesis: pytz extras
        Requires: python3-hypothesis = 6.6.0-1.fc35
        %description -n python3-hypothesis+pytz
        This is a metapackage bringing in pytz extras requires for python3-hypothesis.
        It makes sure the dependencies are installed.
        """).lstrip().splitlines()
    assert lines == expected


@pytest.mark.parametrize('basename_len', [1, 10, 30, 45, 78])
@pytest.mark.parametrize('extra_len', [1, 13, 28, 52, 78])
def test_python_extras_subpkg_description_wrapping(basename_len, extra_len):
    basename = 'x' * basename_len
    extra = 'y' * extra_len
    lines = rpm_eval(f'%python_extras_subpkg -n {basename} -F {extra}',
                     version='6', release='7')
    for idx, line in enumerate(lines):
        if line.startswith('%description'):
            start = idx + 1
    lines = lines[start:]
    assert all(len(l) < 80 for l in lines)
    assert len(lines) < 6
    if len(" ".join(lines[:-1])) < 80:
        assert len(lines) == 2
    expected_singleline = (f"This is a metapackage bringing in {extra} extras "
                           f"requires for {basename}. "
                           f"It makes sure the dependencies are installed.")
    description_singleline = " ".join(lines)
    assert description_singleline == expected_singleline


unversioned_macros = pytest.mark.parametrize('macro', [
    '%__python',
    '%python',
    '%python_version',
    '%python_version_nodots',
    '%python_sitelib',
    '%python_sitearch',
    '%python_platform',
    '%python_platform_triplet',
    '%python_ext_suffix',
    '%py_shebang_fix',
    '%py_build',
    '%py_build_egg',
    '%py_build_wheel',
    '%py_install',
    '%py_install_egg',
    '%py_install_wheel',
    '%py_check_import',
])


@unversioned_macros
def test_unversioned_python_errors(macro):
    lines = rpm_eval(macro, fails=True)
    assert lines == ['error: attempt to use unversioned python, '
                     'define %__python to /usr/bin/python2 or /usr/bin/python3 explicitly']


@unversioned_macros
def test_unversioned_python_works_when_defined(macro):
    macro3 = macro.replace('python', 'python3').replace('py_', 'py3_')
    assert rpm_eval(macro, __python='/usr/bin/python3') == rpm_eval(macro3)


# we could rework the test for multiple architectures, but the Fedora CI currently only runs on x86_64
x86_64_only = pytest.mark.skipif(platform.machine() != "x86_64", reason="works on x86_64 only")


@x86_64_only
def test_platform_triplet():
    assert rpm_eval("%python3_platform_triplet") == ["x86_64-linux-gnu"]


@x86_64_only
def test_ext_suffix():
    assert rpm_eval("%python3_ext_suffix") == [f".cpython-{XY}-x86_64-linux-gnu.so"]


def test_python_sitelib_value():
    macro = '%python_sitelib'
    assert rpm_eval(macro, __python='/usr/bin/python3.6') == [f'/usr/lib/python3.6/site-packages']
    assert rpm_eval(macro, __python='%__python3') == [f'/usr/lib/python{X_Y}/site-packages']


def test_python3_sitelib_value():
    macro = '%python3_sitelib'
    assert rpm_eval(macro, __python3='/usr/bin/python3.6') == [f'/usr/lib/python3.6/site-packages']
    assert rpm_eval(macro) == [f'/usr/lib/python{X_Y}/site-packages']


def test_python_sitearch_value(lib):
    macro = '%python_sitearch'
    assert rpm_eval(macro, __python='/usr/bin/python3.6') == [f'/usr/{lib}/python3.6/site-packages']
    assert rpm_eval(macro, __python='%__python3') == [f'/usr/{lib}/python{X_Y}/site-packages']


def test_python3_sitearch_value(lib):
    macro = '%python3_sitearch'
    assert rpm_eval(macro, __python3='/usr/bin/python3.6') == [f'/usr/{lib}/python3.6/site-packages']
    assert rpm_eval(macro) == [f'/usr/{lib}/python{X_Y}/site-packages']


@pytest.mark.parametrize(
    'args, expected_args',
    [
        ('six', 'six'),
        ('-f foo.txt', '-f foo.txt'),
        ('-t -f foo.txt six, seven', '-t -f foo.txt six, seven'),
        ('-e "foo*" -f foo.txt six, seven', '-e "foo*" -f foo.txt six, seven'),
        ('six.quarter six.half,, SIX', 'six.quarter six.half,, SIX'),
        ('-f foo.txt six\nsix.half\nSIX', '-f foo.txt six six.half SIX'),
        ('six \\ -e six.half', 'six -e six.half'),
    ]
)
@pytest.mark.parametrize('__python3',
                         [None,
                          f'/usr/bin/python{X_Y}',
                          '/usr/bin/python3.6'])
def test_py3_check_import(args, expected_args, __python3, lib):
    x_y = X_Y
    macros = {
        'buildroot': 'BUILDROOT',
        '_rpmconfigdir': 'RPMCONFIGDIR',
        'py3_shebang_flags': 's',
    }
    if __python3 is not None:
        macros['__python3'] = __python3
        # If the __python3 command has version at the end, parse it and expect it.
        # Note that the command is used to determine %python3_sitelib and %python3_sitearch,
        # so we only test known CPython schemes here and not PyPy for simplicity.
        # We also only test main Python + 3.6 because those are required by the CI config.
        if (match := re.match(r'.+python(\d+\.\d+)$', __python3)):
            x_y = match.group(1)

    invocation = '%{py3_check_import ' + args +'}'
    lines = rpm_eval(invocation, **macros)

    # An equality check is a bit inflexible here,
    # every time we change the macro we need to change this test.
    # However actually executing it and verifying the result is much harder :/
    # At least, let's make the lines saner to check:
    lines = [line.rstrip('\\').strip() for line in lines]
    expected = textwrap.dedent(fr"""
        PATH="BUILDROOT/usr/bin:$PATH"
        PYTHONPATH="${{PYTHONPATH:-BUILDROOT/usr/{lib}/python{x_y}/site-packages:BUILDROOT/usr/lib/python{x_y}/site-packages}}"
        PYTHONDONTWRITEBYTECODE=1
        {__python3 or '/usr/bin/python3'} -s RPMCONFIGDIR/redhat/import_all_modules.py {expected_args}
        """)
    assert lines == expected.splitlines()


@pytest.mark.parametrize(
    'shebang_flags_value, expected_shebang_flags',
    [
        ('s', '-s'),
        ('%{nil}', ''),
        (None, ''),
        ('Es', '-Es'),
    ]
)
def test_py3_check_import_respects_shebang_flags(shebang_flags_value, expected_shebang_flags, lib):
    macros = {
        '_rpmconfigdir': 'RPMCONFIGDIR',
        '__python3': '/usr/bin/python3',
        'py3_shebang_flags': shebang_flags_value,
    }
    lines = rpm_eval('%py3_check_import sys', **macros)
    # Compare the last line of the command, that's where lua part is evaluated
    expected = f'/usr/bin/python3 {expected_shebang_flags} RPMCONFIGDIR/redhat/import_all_modules.py sys'
    assert  lines[-1].strip() == expected
