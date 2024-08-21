from pydantic import BaseModel
import typer
from pypi_simple import PyPISimple, ProjectPage

app = typer.Typer()

class Package(BaseModel):
   build: str = ""
   build_number: int = 0
   depends: list[str] = []
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
      # provenance = pypi.get_provenance(package)
      pkg_sha256 = package.digests.get("sha256")
      return package.filename, Package(
        name=package.project,
        version=package.version,
        sha256=pkg_sha256
      )
  return "0.0.0", Package()



@app.command()
def create_api(
    package_name: str = typer.Option(..., help="The name of the package."),
    version: str = typer.Option(..., help="The version of the package."),
    output_file: str = typer.Option("synthetic_repodata.json", help="The output file to save the synthetic repodata.json.")
):
    """
    Create a repodata.json file based on the list of projects provided.
    """

    conda_style_packages = {}
    # Make an API request to PyPI
    try:
        project_page = pypi.get_project_page(package_name)
        full_name, package = extract_version_of_project(project_page, version)
        # print(package)
        conda_style_packages.update({full_name: package})


    except Exception as e:
        typer.echo(f"Error fetching package info: {e}")
        return

    # Create API definition
    repodata = RepoData(
        info={"subdir": "osx-arm64"}, # default for now
        packages=conda_style_packages,
        # "packages.conda": [package_name],
        # "pypi_info": package_info,
        repodata_version=1
    )

    # Save to output file
    with open(output_file, "w") as f:
        f.write(repodata.model_dump_json(indent=2))
    typer.echo(f"Repodata saved to {output_file}")

if __name__ == "__main__":
    # Initialize PyPISimple, kind of global
    pypi = PyPISimple()
    app()