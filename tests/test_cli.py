from __future__ import annotations

import pytest
from click.testing import CliRunner

from conda_pupa.cli import cli


def test_cli(tmp_path):
    """
    Coverage testing for the cli.
    """

    runner = CliRunner()

    # mutually exclusive
    result = runner.invoke(
        cli,
        ["-b=.", "-e=."],
    )

    print(result.stdout)

    assert result.exit_code != 0
    assert "Error:" in result.stdout and "exclusive" in result.stdout

    # build editable, ordinary wheel
    for kind, option in ("editable", "-e"), ("wheel", "-b"):
        output_path = tmp_path / kind
        output_path.mkdir()
        result = runner.invoke(cli, [option, ".", "--output-folder", output_path])
        assert len(list(output_path.glob("*.conda"))) == 1
