"""
Fetch matching wheels from pypi.
"""

import subprocess
import sys
from pathlib import Path

from conda.models.match_spec import MatchSpec
from pypi_simple import PyPISimple

from conda_pupa.translate import conda_to_requires


def download_pypi_pip(matchspec: MatchSpec, target_path: Path):
    """
    Prototype download wheel for missing package using pip.

    Complete implementation should match wheels based on target environment at
    least, directly use pypi API instead of pip.
    """
    requirement = conda_to_requires(matchspec)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--only-binary",
            ":all:",
            "-w",
            str(target_path),
            str(requirement),
        ],
        check=True,
    )


def download_pypi_nopip(matchspec: MatchSpec):
    """
    (What could become) lower level download wheel for missing package not using pip.

    Would not require pip to be installed in the target environment, for one.

    Complete implementation should match wheels based on target environment at
    least, directly use pypi API instead of pip.
    """
    # Code lifted from corpus.py
    with PyPISimple() as client:
        try:
            page = client.get_project_page(package.name)
        except pypi_simple.errors.NoSuchProjectError as e:
            print(package.name, e)
            return
        # TODO code to skip already-fetched projects
        for pkg in page.packages:
            if pkg.version != package.version:
                print(pkg.version, "!=", package.version)
                return
            if pkg.has_metadata is not None:
                print("Has metadata?", pkg.has_metadata)
                try:
                    src = client.get_package_metadata(pkg)
                except NoMetadataError:
                    print(f"{pkg.filename}: No metadata available")
                else:
                    print(pkg)
                    # avoid unique errors
                    session.execute(
                        pypi_metadata.delete().where(
                            pypi_metadata.c.filename == pkg.filename
                        )
                    )
                    session.execute(
                        pypi_metadata.insert().values(
                            filename=pkg.filename,
                            name=pkg.project,
                            version=pkg.version,
                            metadata=src,
                        )
                    )
            else:
                print(f"{pkg.filename}: No metadata available")
            print()
