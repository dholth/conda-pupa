import re
from typing import Optional

import packaging
import typer
import yaml
from pydantic import BaseModel
from pypi_simple import ProjectPage, PyPISimple

from conda_pupa.translate import FileDistribution, requires_to_conda


# warning: hacky
def parse_match_spec(spec: str):
    pattern = (
        r"(?P<name>[a-zA-Z0-9_\-]+)(?P<operator>[<>=!~]{1,2})\s*(?P<version>[0-9\.]+)"
    )
    match = re.match(pattern, spec.strip())
    if match:
        return match.groupdict()
    else:
        raise ValueError("Invalid match spec")


app = typer.Typer()


class Package(BaseModel):
    build: str = ""
    build_number: int = 0
    depends: list[str] = []
    extras: dict[str, list[str]] = {}
    md5: str = ""
    name: str = ""
    sha256: str = ""
    size: int = 0
    subdir: str = ""
    timestamp: int = 0
    version: str = ""


class RepoData(BaseModel):
    info: dict
    packages: dict[str, Package]
    # "packages.conda": list[str]
    # remove: list[Package]
    repodata_version: int


def extract_version_of_project(project_page: ProjectPage, version: str):
    """
    Extract the version and details of the project from the project page.
    """
    for package in project_page.packages:
        if package.version == version:
            package_metadata = pypi.get_package_metadata(package)
            package_data = FileDistribution(package_metadata)

            requirements, extras = requires_to_conda(package_data.requires)

            python_version = package_data.metadata["requires-python"]
            requires_python = "python"
            if python_version:
                requires_python = f"python { python_version }"
            depends = [requires_python] + requirements

            # provenance = pypi.get_provenance(package)
            pkg_sha256 = package.digests.get("sha256")
            return package.filename, Package(
                name=package.project,
                version=package.version,
                sha256=pkg_sha256,
                depends=depends,
                extras=extras,
            )
    return "0.0.0", Package()


def convert_to_repodata_package(
    package_name: str, version: str, conda_style_packages: dict = {}
):
    packages_dict = conda_style_packages.copy()
    project_page = pypi.get_project_page(package_name)
    full_name, package = extract_version_of_project(project_page, version)
    packages_dict.update({full_name: package})
    return packages_dict


@app.command()
def create_synthetic_repodata_json(
    package_name: Optional[str] = typer.Option(None, help="The name of the package."),
    input_file: str = typer.Option(
        "environment.yml", help="The name of the conda environment.yml file."
    ),
    version: Optional[str] = typer.Option(None, help="The version of the package."),
    output_file: str = typer.Option(
        "synthetic_repodata.json",
        help="The output file to save the synthetic repodata.json.",
    ),
):
    """
    Create a repodata.json file based on the list of projects provided.
    """

    conda_style_packages = {}
    # Make an API request to PyPI
    try:
        if package_name:
            conda_style_packages = convert_to_repodata_package(
                package_name, version, conda_style_packages
            )
        elif input_file:
            with open(input_file, "r") as file:
                data = yaml.safe_load(file)
                pip_deps = data.get("dependencies")[-1].get(
                    "pip"
                )  # the pip: key must be last
            for dep in pip_deps:
                spec_details = parse_match_spec(dep)
                package_name = spec_details.get("name")
                # op
                version = spec_details.get("version")
                conda_style_packages = convert_to_repodata_package(
                    package_name, version, conda_style_packages
                )

    except Exception as e:
        typer.echo(f"Error fetching package info: {e}")
        raise e

    # Create API definition
    repodata = RepoData(
        info={"subdir": "osx-arm64"},  # default for now
        packages=conda_style_packages,
        # "packages.conda": [package_name],
        # "pypi_info": package_info,
        repodata_version=1,
    )

    # Save to output file
    with open(output_file, "w") as f:
        f.write(repodata.model_dump_json(indent=2))
    typer.echo(f"Repodata saved to {output_file}")


if __name__ == "__main__":
    # Initialize PyPISimple, kind of global
    pypi = PyPISimple()
    app()
