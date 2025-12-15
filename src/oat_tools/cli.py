import click

from pathlib import Path
from oat_tools.wordcounter import print_file_word_counts
from oat_tools.references import (
    MarkdownFile,
    print_references_table,
    print_orphan_references,
)
from oat_tools.captions import (
    CaptionFile,
    print_caption_status,
    fix_caption_files,
)


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


@references.command("check")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def references_check(files):
    """
    Check for unused references and show ordering by first appearance.

    Args:
        files: Markdown files to check for reference issues.
    """

    # Create MarkdownReferenceManager instances for each file
    markdown_files = []
    for file in files:
        file_path = Path(str(file))
        md = MarkdownFile(file_path)
        markdown_files.append(md)

    # Print the references table
    print_references_table(markdown_files)
    print_orphan_references(markdown_files)


@references.command("fix")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def references_fix(files):
    """
    Fix reference issues by removing unused references and reordering by first appearance.

    WARNING: This modifies files in place. Use with caution.

    Args:
        files: Markdown files to fix reference issues in.
    """
    for file in files:
        file_path = Path(str(file))
        md = MarkdownFile(file_path)
        md.fix_references()


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def wordcount(files: list[click.Path]):
    """
    Count words in Markdown files, excluding code blocks, footnotes, and URLs.

    Args:
        files: Markdown files to count words in.
    """

    file_paths = [Path(str(f)) for f in files]
    print_file_word_counts(file_paths)


@cli.group()
def captions():
    """
    Manage caption numbering in Markdown files.
    """
    pass


@captions.command("check")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def captions_check(files):
    """
    Check if captions are numbered correctly in Markdown files.

    Captions should follow the format: **Kuva #**: Caption text
    and be numbered sequentially starting from 1.

    Args:
        files: Markdown files to check for caption issues.
    """
    caption_files = []
    for file in files:
        file_path = Path(str(file))
        cf = CaptionFile(file_path)
        caption_files.append(cf)

    print_caption_status(caption_files)


@captions.command("fix")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def captions_fix(files):
    """
    Fix caption numbering in Markdown files.

    Renumbers captions sequentially starting from 1.
    WARNING: This modifies files in place. Use with caution.

    Args:
        files: Markdown files to fix caption numbering in.
    """
    caption_files = []
    for file in files:
        file_path = Path(str(file))
        cf = CaptionFile(file_path)
        caption_files.append(cf)

    fix_caption_files(caption_files)
