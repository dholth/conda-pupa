"""
Run under target Python interpreter to get dependencies using pypa/build.

Alternative implementation would use conda PrefixData plus conda/pypi name
translation; but this one supports extras and the format in pyproject.toml.
"""

import json
import sys

import build


def check_dependencies(build_system_requires):
    missing = [u for d in build_system_requires for u in build.check_dependency(d)]
    return missing


if __name__ == "__main__":
    name, flag, requirements = sys.argv
    assert flag == "-r"
    requirements = json.loads(requirements)
    stuff = check_dependencies(requirements)
    print(json.dumps(stuff))
