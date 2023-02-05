"""Performs automation using the powerful `nox` automation tool."""
import glob
import json
import sys
from contextlib import suppress

import nox


PYTHON_VERSIONS_FILE = "pyversions.json"
try:
    with open(PYTHON_VERSIONS_FILE, "r", encoding="utf8") as f:
        python_versions_dict = json.load(f)
except Exception:
    print(
        "Please ensure Python executable paths are configured correctly in",
        PYTHON_VERSIONS_FILE)
    sys.exit(1)
PYTHON_VERSIONS = tuple(python_versions_dict.values())


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Lints all library source code."""
    session.install("pylint")
    for module in glob.glob("equake/*.py"):
        with suppress(Exception):
            session.run("pylint", module)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Runs all tests."""
    for module in glob.glob("testing/*.py"):
        if module.split("\\")[-1].startswith("test"):
            session.run("python", module)
