import click

from oat_tools.references import ReferenceCollection

@click.group()
def cli():
    """
    Command line interface for OAT tools.
    """
    pass

@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def list_files(files):
    """
    List files matching a glob pattern.

    Args:
        glob (str): The glob pattern to match files against.
    """
    print("Listing files:")
    for file in files:
        print(file)