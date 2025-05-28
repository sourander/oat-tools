import click

from pathlib import Path
from oat_tools.wordcounter import print_file_word_counts
from oat_tools.references import MarkdownReferenceManager, print_references_table, print_orphan_references

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
    
    # Create MarkdownReferenceManager instances for each file
    reference_managers = []
    for file in files:
        file_path = Path(str(file))
        manager = MarkdownReferenceManager(file_path)
        reference_managers.append(manager)
    
    # Print the references table
    print_references_table(reference_managers)
    print_orphan_references(reference_managers)

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
def wordcount(files: list[click.Path]):
    """
    Count words in Markdown files, excluding code blocks, footnotes, and URLs.
    
    Args:
        files: Markdown files to count words in.
    """
    click.echo("Counting words in files:")

    file_paths = [Path(str(f)) for f in files]
    
    print_file_word_counts(file_paths)