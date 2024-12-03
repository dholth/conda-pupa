"""
Command line interface for conda-pupa.
"""

import click

import conda_pupa.editable


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-c",
    "--channel",
    help="Additional channel to search for packages.",
    multiple=True,
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
@click.option("-n", "--name", help="Name of environment.", required=False)
def cli(channel, editable, prefix, name):
    print(channel, editable, prefix, name)

    if editable:
        conda_pupa.editable.editable(editable)
