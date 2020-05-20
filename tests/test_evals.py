import subprocess
import sys


def rpm_eval(expression, **kwargs):
    cmd = ['rpmbuild']
    for var, value in kwargs.items():
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
    assert len(lines) == 2


def test_python_provide_python3_epoched():
    lines = rpm_eval('%python_provide python3-foo', epoch='1', version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert len(lines) == 2


def test_python_provide_doubleuse():
    lines = rpm_eval('%{python_provide python3-foo}%{python_provide python3-foo}',
                     version='6', release='1.fc66')
    assert 'Obsoletes: python-foo < 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert len(lines) == 4
    assert len(set(lines)) == 2


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
    assert len(lines) == 2


def test_py_provides_python3_epoched():
    lines = rpm_eval('%py_provides python3-foo', epoch='1', version='6', release='1.fc66')
    assert 'Provides: python3-foo = 1:6-1.fc66' in lines
    assert 'Provides: python-foo = 1:6-1.fc66' in lines
    assert len(lines) == 2


def test_py_provides_doubleuse():
    lines = rpm_eval('%{py_provides python3-foo}%{py_provides python3-foo}',
                     version='6', release='1.fc66')
    assert 'Provides: python3-foo = 6-1.fc66' in lines
    assert 'Provides: python-foo = 6-1.fc66' in lines
    assert len(lines) == 4
    assert len(set(lines)) == 2


def test_py_provides_with_evr():
    lines = rpm_eval('%py_provides python3-foo 123',
                     version='6', release='1.fc66')
    assert 'Provides: python3-foo = 123' in lines
    assert 'Provides: python-foo = 123' in lines
    assert len(lines) == 2
