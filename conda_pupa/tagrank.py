"""
Compatible tags versus a wheel's tags ranking algorithm.
"""

import pickle
import subprocess
import sys

import pypi_simple.errors
from packaging.tags import Tag, sys_tags
from packaging.utils import parse_wheel_filename
from pypi_simple import NoMetadataError, PyPISimple


def foreign_tags(python_exe):
    """
    Call packaging.tags in another interpreter.

    The in-process packaging.tags can also generate these if given information about the other interpreter...
    """
    result = subprocess.run([python_exe, "-c", "import sys,pickle,packaging.tags;sys.stdout.buffer.write(pickle.dumps((*packaging.tags.sys_tags(),)))"], capture_output=True, check=True)
    tags = pickle.loads(result.stdout)
    return tags


def best_wheel_for(pname, tags: list[Tag]):
    """
    Find best ranked compatible wheel by tags for each available version.
    """
    class package:
        name=pname

    with PyPISimple() as client:
        try:
            page = client.get_project_page(package.name)
        except pypi_simple.errors.NoSuchProjectError as e:
            print(package.name, e)
            return

        by_version = {}
        for pkg in page.packages:
            by_version[pkg.version] = by_version.get(pkg.version, []) + [pkg]

        # find newest version matching requested spec

        # find all wheels

        # find best wheel matching spec and tags

        # for pkg in page.packages:
        #     if pkg.version != package.version:
        #         print(pkg.version, "!=", package.version)
        #         return
        #     if pkg.has_metadata is not None:
        #         print("Has metadata?", pkg.has_metadata)
        #         try:
        #             src = client.get_package_metadata(pkg)
        #         except NoMetadataError:
        #             print(f"{pkg.filename}: No metadata available")
        #         else:
        #             print(pkg)
        #             # avoid unique errors
        #             session.execute(
        #                 pypi_metadata.delete().where(
        #                     pypi_metadata.c.filename == pkg.filename
        #                 )
        #             )
        #             session.execute(
        #                 pypi_metadata.insert().values(
        #                     filename=pkg.filename,
        #                     name=pkg.project,
        #                     version=pkg.version,
        #                     metadata=src,
        #                 )
        #             )
        #     else:
        #         print(f"{pkg.filename}: No metadata available")
        #     print()

    return by_version


if __name__ == "__main__":
    python_exe = sys.argv[1]
    tags = foreign_tags(python_exe)
    best_wheel_for("sqlalchemy", tags)
