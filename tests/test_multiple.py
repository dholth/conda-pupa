"""
Test converting a dependency tree to conda.
"""

import json
import os
import pathlib
import subprocess

from conda.models.match_spec import MatchSpec

from conda_pupa.convert_tree import ConvertTree

REPO = pathlib.Path(__file__).parents[1] / "synthetic_repo"


def list_envs():
    output = subprocess.run(
        f"{os.environ['CONDA_EXE']} info --envs --json".split(),
        capture_output=True,
        check=True,
    )
    env_info = json.loads(output.stdout)
    return env_info


def create_test_env(name):
    """
    Create named environment if it does not exist.
    """
    envs = list_envs()
    if not any((e.endswith(f"{os.sep}{name}") for e in envs["envs"])):
        subprocess.run(
            [os.environ["CONDA_EXE"], "create", "-n", name, "-y", "python 3.12"],
            check=True,
            encoding="utf-8",
        )
    return envs


def test_multiple(tmp_path):
    """
    Install multiple only-available-from-pypi dependencies into an environment.
    """
    TARGET_ENV = "pupa-target"

    # defeat local cache. This test also uses a persistent TARGET_ENV; delete
    # manually if done before expected.
    CONDA_PKGS_DIRS = tmp_path / "conda-pkgs"
    CONDA_PKGS_DIRS.mkdir()
    env = os.environ.copy()
    env["CONDA_PKGS_DIRS"] = str(CONDA_PKGS_DIRS)

    WHEEL_DIR = tmp_path / "wheels"
    WHEEL_DIR.mkdir(exist_ok=True)

    REPO.mkdir(parents=True, exist_ok=True)

    envs_dict = create_test_env(TARGET_ENV)
    TARGET_ENV_PATH = next(e for e in envs_dict["envs"] if e.endswith(TARGET_ENV))

    TARGET_DEP = MatchSpec("twine==5.1.1")  # type: ignore

    converter = ConvertTree(TARGET_ENV_PATH, repo=REPO, override_channels=True)
    converter.convert_tree([TARGET_DEP])
