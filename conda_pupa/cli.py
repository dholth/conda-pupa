"""
Command line interface for conda-pupa.
"""

import click


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
    help="Install local directory as editable package.",
)
def cli(channel, editable):
    print(channel, editable)
