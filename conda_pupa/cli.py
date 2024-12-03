"""
Command line interface for conda-pupa.
"""

from pathlib import Path

import click

import conda_pupa.convert_tree
import conda_pupa.editable


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-c",
    "--channel",
    help="Additional channel to search for packages.",
    multiple=True,
)
@click.option(
    "-O",
    "--override-channels",
    help="Do not search default or .condarc channels. Will search pypi.",
)
@click.option(
    "-e",
    "--editable",
    required=False,
    help="Build named path as editable package; install to link checkout to environment.",
)
@click.option(
    "-p",
    "--prefix",
    help="Full path to environment location (i.e. prefix).",
    required=False,
)
@click.argument(
    "package_spec",
    nargs=-1,
)
@click.option("-n", "--name", help="Name of environment.", required=False)
def cli(channel, editable, prefix, name, override_channels, package_spec):
    print(channel, editable, prefix, name)

    if editable:
        conda_pupa.editable.editable(editable)

    else:
        if prefix:
            prefix = Path(prefix).expanduser()
        # XXX or environment name plus default prefix

        converter = conda_pupa.convert_tree.ConvertTree(
            prefix, override_channels=override_channels
        )
        converter.convert_tree(package_spec)
