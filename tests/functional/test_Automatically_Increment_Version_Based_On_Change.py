"""Automatically Increment Version Based On Change feature tests."""
import os
from pathlib import Path

import tomli
from pytest_bdd import given, scenario, then, when

from pycodegen.coder import Coder, bump_version

repo_owner = "myrontuttle"
test_repo = "test_project"
test_issue = 3


@scenario(
    "../features/Automatically_Increment_Version_Based_On_Change.feature",
    "Automatically Increment Version",
)
def test_automatically_increment_version():
    """Automatically Increment Version."""


@given("a code change for an issue")
def code_change_for_issue():
    """a code change for an issue."""


@when("the coder finishes work on that issue")
def coder_finishes_work_on_issue():
    """the coder finishes work on that issue."""


@then("the project version is updated based on the work")
def update_project_version():
    """the project version is updated based on the work."""
    coder = Coder(repo_owner, test_repo)
    os.chdir(coder.repo_path)
    bump_version("feature")
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
    version = pyproject["project"]["version"]
    assert version == "0.1.0"
    bump_version("bug")
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
    new_version = pyproject["project"]["version"]
    assert new_version == "0.1.1"
    # Note, you need to manually reset the version in pyproject.toml
