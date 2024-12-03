"""
Compatible tags versus a wheel's tags ranking algorithm.
"""

import pickle
import pprint
import subprocess
import sys
from pathlib import Path

import pypi_simple.errors
from packaging.requirements import Requirement
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from packaging.version import Version
from pypi_simple import DistributionPackage, NoMetadataError, PyPISimple


def foreign_tags(python_exe):
    """
    Call packaging.tags in another interpreter.

    The in-process packaging.tags can also generate these if given information about the other interpreter...
    """
    result = subprocess.run(
        [
            python_exe,
            "-c",
            "import sys,pickle,packaging.tags;sys.stdout.buffer.write(pickle.dumps((*packaging.tags.sys_tags(),)))",
        ],
        capture_output=True,
        check=True,
    )
    tags = pickle.loads(result.stdout)
    return tags


def fetch_package_page(pname, tags: list[Tag]):
    """
    Return all packages for a distribution name.
    """

    class package:
        name = pname

    with PyPISimple() as client:
        try:
            page = client.get_project_page(package.name)
        except pypi_simple.errors.NoSuchProjectError as e:
            print(package.name, e)
            return

        return page.packages


def rank_packages(packages: list[DistributionPackage]):
    by_version: dict[str | None, list[DistributionPackage]] = {}
    for pkg in packages:
        by_version[pkg.version] = by_version.get(pkg.version, []) + [pkg]

    # XXX pass in "pagage > 4" or "package == 1.2" specifier, filter
    by_version_sorted = sorted(((Version(v), v) for v in by_version if v), reverse=True)

    best_supported_by_version: dict[tuple[Version, int], DistributionPackage] = {}
    for version, v in by_version_sorted:
        for pkg in by_version[v]:
            if pkg.package_type == "wheel":
                wheel_name, wheel_version, wheel_build, wheel_tags = (
                    parse_wheel_filename(pkg.filename)
                )
                # they don't seem to == even if str(t1) == str(t2); pickle problem or ??
                wheel_tags = {str(tag) for tag in wheel_tags}
                for rank, tag in enumerate(tags):
                    if str(tag) in wheel_tags:
                        # Assign rank to all supported wheels with same version
                        best_supported_by_version[(version, -rank)] = pkg

    # "some version in SpecifierSet"

    # find newest version matching requested spec

    # find all wheels

    # find best wheel matching spec and tags

    return best_supported_by_version


if __name__ == "__main__":
    python_exe = sys.argv[1]
    tags = foreign_tags(python_exe)

    # if False:
    #     packages = fetch_package_page("sqlalchemy", tags)
    # else:
    #     packages = pickle.loads(Path("packages.pickle").read_bytes())

    # pprint.pprint(rank_packages(packages))
