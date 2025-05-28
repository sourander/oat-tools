import click

from oat_tools.references import ReferenceCollection

@click.group()
def cli():
    """
    Command line interface for OAT tools.
    """
    pass

@cli.group()
def references():
    """
    Manage Vancouver style references in Markdown files.
    """
    pass

@references.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
def check(files):
    """
    Check for unused references and show ordering by first appearance.
    
    Args:
        files: Markdown files to check for reference issues.
    """
    click.echo("Checking references in files:")
    for file in files:
        click.echo(f"  - {file}")
    # TODO: Implement reference checking logic
    click.echo("Reference checking not yet implemented.")

@references.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
def fix(files):
    """
    Fix reference issues by removing unused references and reordering.
    
    WARNING: This modifies files in place. Use with caution.
    
    Args:
        files: Markdown files to fix reference issues in.
    """
    click.echo("Fixing references in files:")
    for file in files:
        click.echo(f"  - {file}")
    # TODO: Implement reference fixing logic
    click.echo("Reference fixing not yet implemented.")

@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
def wordcount(files):
    """
    Count words in Markdown files, excluding code blocks, footnotes, and URLs.
    
    Args:
        files: Markdown files to count words in.
    """
    click.echo("Counting words in files:")
    for file in files:
        click.echo(f"  - {file}")
    # TODO: Implement word counting logic
    click.echo("Word counting not yet implemented.")