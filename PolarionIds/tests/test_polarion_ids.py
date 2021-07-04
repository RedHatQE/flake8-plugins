# flake8: noqa PID001,PID002

import os
import re
from subprocess import PIPE, Popen

import pytest

# Test function tests
test_empty_polarion_id_content = """
import pytest


@pytest.mark.polarion()
def test_empty_polarion_id():
    pass
"""


test_no_polarion_id_content = """
def test_no_polarion_id():
    pass
"""

test_wrong_polarion_id_content = """
import pytest


@pytest.mark.polarion("CNVV-2350")
def test_wrong_polarion_id():
    pass
"""

test_with_polarion_id_content = """
import pytest


@pytest.mark.polarion("CNV-2350")
def test_with_polarion_id():
    pass
"""

# Test parameterized tests
test_parameterized_no_polarion_id_content = """
import pytest


@pytest.mark.parametrize(
    "param",
    [pytest.param('parametrize_no_polarion_id')]
)
def test_parameterized_no_polarion_id(param):
    pass
"""

test_parameterized_wrong_polarion_id_content = """
import pytest


@pytest.mark.parametrize(
    "param",
    [pytest.param('parametrize_wrong_polarion_id', marks=(pytest.mark.polarion("CNVV-2350")))]
)
def test_parameterized_wrong_polarion_id(param):
    pass
"""

test_parameterized_with_polarion_id_content = """
import pytest


@pytest.mark.parametrize(
    "param",
    [pytest.param("parametrize_with_polarion_id", marks=(pytest.mark.polarion("CNV-2072")))]
)
def test_parameterized_with_polarion_id(param):
    pass
"""

test_parameterized_no_polarion_id_with_non_polarion_mark_content = """
import pytest


@pytest.mark.parametrize(
    "param",
    [
        pytest.param('parametrize_no_polarion_id_with_non_polarion_mark', marks=(pytest.mark.bugzilla(1716905)))
    ],
)
def test_parameterized_no_polarion_id_with_non_polarion_mark(param):
    pass
"""

test_mixed_parameterized_content = """
import pytest


@pytest.mark.parametrize(
    "param",
    [
        pytest.param('parametrize_no_polarion_id'),
        pytest.param('parametrize_no_polarion_id_with_non_polarion_mark', marks=(pytest.mark.bugzilla(1716905))),
        pytest.param('parametrize_wrong_polarion_id', marks=(pytest.mark.polarion("CNVV-2350"))),
        pytest.param("parametrize_with_polarion_id", marks=(pytest.mark.polarion("CNV-2072")))
    ],
)
def test_mixed_parameterized(param):
    pass
"""

# Test tests in class
test_class_no_polarion_id_content = """
class Test:
    def test_class_no_polarion_id(self):
        pass
"""

test_class_wrong_polarion_id_content = """
import pytest


class Test:
    @pytest.mark.polarion("CNVV-2350")
    def test_class_wrong_polarion_id(self):
        pass
"""

test_class_with_polarion_id_content = """
import pytest


class Test:
    @pytest.mark.polarion("CNV-2350")
    def test_class_with_polarion_id(self):
        pass
"""

test_class_parameterized_mixed_content = """
import pytest


class Test:
    @pytest.mark.parametrize(
        "param",
        [
            pytest.param('parametrize_no_polarion_id'),
            pytest.param('parametrize_no_polarion_id_with_non_polarion_mark', marks=(pytest.mark.bugzilla(1716905))),
            pytest.param('parametrize_wrong_polarion_id', marks=(pytest.mark.polarion("CNVV-2350"))),
            pytest.param("parametrize_with_polarion_id", marks=(pytest.mark.polarion("CNV-2072")))
        ],
    )
    def test_class_parameterized_mixed(self, param):
        pass
"""

# Polarion ID on parameterized fixture
test_fixture_parameterized_content = """
import pytest


@pytest.fixture(
    params=[
        pytest.param('parametrize_no_polarion_id'),
        pytest.param('parametrize_no_polarion_id_with_non_polarion_mark', marks=(pytest.mark.bugzilla(1716905))),
        pytest.param('parametrize_wrong_polarion_id', marks=(pytest.mark.polarion("CNVV-2350"))),
        pytest.param("parametrize_with_polarion_id", marks=(pytest.mark.polarion("CNV-2072")))
    ],
)
def params_fixture():
    pass


@pytest.fixture()
def dummy():
    pass


def test_fixture_parameterized(params_fixture, dummy):
    pass
"""

test_fixture_parameterized_as_list_content = """
import pytest


@pytest.fixture(
    params=[
        pytest.param(['parametrize_no_polarion_id']),
        pytest.param(['parametrize_no_polarion_id_with_non_polarion_mark'], marks=(pytest.mark.bugzilla(1716905))),
        pytest.param(['parametrize_wrong_polarion_id'], marks=(pytest.mark.polarion("CNVV-2350"))),
        pytest.param(["parametrize_with_polarion_id"], marks=(pytest.mark.polarion("CNV-2072")))
    ],
)
def params_fixture():
    pass


@pytest.fixture()
def dummy():
    pass


def test_fixture_parameterized(params_fixture, dummy):
    pass
"""


def prepare_test_file(tmp_test_file, test_name, file_content):
    tmp_test_file.write(file_content.format(test_name=test_name))
    tmp_test_file.read()
    return tmp_test_file.name


@pytest.fixture()
def tmp_test_file(tmpdir):
    test_file_name = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), f"{tmpdir}/test_file.py"
    )
    with open(test_file_name, "w+") as test_file:
        yield test_file
    os.remove(test_file_name)


def check_polarion_ids_plugin(test_file_name):
    out, _ = Popen(
        ["flake8", "--enable-extensions=PID", test_file_name], stdout=PIPE, stderr=PIPE
    ).communicate()
    return out.decode("utf-8")


def check_pid001(flake8_out):
    assert re.findall(r"PID001: .*, Polarion ID is missing", flake8_out)


def check_pid002(flake8_out):
    assert re.findall(r"PID002: .*, Polarion ID is wrong", flake8_out)


# Test function tests
def test_empty_polarion_id(tmp_test_file):
    test_name = "test_empty_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid001(out)


def test_no_polarion_id(tmp_test_file):
    test_name = "test_no_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid001(out)


def test_wrong_polarion_id(tmp_test_file):
    test_name = "test_wrong_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid002(out)


def test_with_polarion_id(tmp_test_file):
    test_name = "test_with_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    assert not out


# Test parameterized tests
def test_parameterized_no_polarion_id(tmp_test_file):
    test_name = "test_parameterized_no_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid001(out)


def test_parameterized_wrong_polarion_id(tmp_test_file):
    test_name = "test_parameterized_wrong_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid002(out)


def test_parameterized_with_polarion_id(tmp_test_file):
    test_name = "test_parameterized_with_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    assert not out


def test_mixed_parameterized(tmp_test_file):
    test_name = "test_mixed_parameterized"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )

    out = check_polarion_ids_plugin(test_file_name)
    out_lines = out.splitlines()
    out_lines.sort()
    assert len(out_lines) == 3
    check_pid001(out_lines[0])
    check_pid002(out_lines[1])
    check_pid001(out_lines[2])


# Test tests in class
def test_class_no_polarion_id(tmp_test_file):
    test_name = "test_class_no_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid001(out)


def test_class_wrong_polarion_id(tmp_test_file):
    test_name = "test_class_wrong_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    check_pid002(out)


def test_class_with_polarion_id(tmp_test_file):
    test_name = "test_class_with_polarion_id"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )
    out = check_polarion_ids_plugin(test_file_name)
    assert not out


def test_class_parameterized_mixed(tmp_test_file):
    test_name = "test_class_parameterized_mixed"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )

    out = check_polarion_ids_plugin(test_file_name)
    out_lines = out.splitlines()
    out_lines.sort()
    assert len(out_lines) == 3
    check_pid001(out_lines[0])
    check_pid002(out_lines[1])
    check_pid001(out_lines[2])


# Polarion ID on parameterized fixture
def test_fixture_parameterized(tmp_test_file):
    test_name = "test_fixture_parameterized"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )

    out = check_polarion_ids_plugin(test_file_name)
    out_lines = out.splitlines()
    out_lines.sort()

    assert len(out_lines) == 3
    check_pid001(out_lines[0])
    check_pid001(out_lines[1])
    check_pid002(out_lines[2])


def test_fixture_parameterized_as_list(tmp_test_file):
    test_name = "test_fixture_parameterized_as_list"
    test_file_name = prepare_test_file(
        tmp_test_file, test_name, eval(f"{test_name}_content")
    )

    out = check_polarion_ids_plugin(test_file_name)
    out_lines = out.splitlines()
    out_lines.sort()
    assert len(out_lines) == 3
    check_pid001(out_lines[0])
    check_pid001(out_lines[1])
    check_pid002(out_lines[2])
