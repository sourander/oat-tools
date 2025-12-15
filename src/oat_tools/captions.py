import re

from dataclasses import dataclass
from pathlib import Path
from tabulate import tabulate


# Pattern to match captions in the format: **Kuva #**: Some caption text
CAPTION_PATTERN = re.compile(r"\*\*Kuva (\d+)\*\*: (.+)")

# Pattern to match malformed captions where colon is inside the bolding
MALFORMED_CAPTION_PATTERN = re.compile(r"\*\*Kuva (\d+):\*\*")


@dataclass
class Caption:
    """
    A class that represents a caption in a Markdown file.

    Attributes:
        line_number (int): The line number where the caption appears (0-indexed).
        current_number (int): The current number of the caption.
        text (str): The caption text after the number.
        full_line (str): The full original line.
    """

    line_number: int
    current_number: int
    text: str
    full_line: str

    def get_renumbered_line(self, new_number: int) -> str:
        """
        Return the caption line with a new number.
        """
        return f"**Kuva {new_number}**: {self.text}"


@dataclass
class CaptionIssue:
    """
    A class to record a caption numbering issue.

    Attributes:
        file_path (Path): The path to the file.
        line_number (int): The line number (1-indexed for display).
        current_number (int): The current caption number.
        expected_number (int): The expected caption number.
        caption_text (str): The caption text.
    """

    file_path: Path
    line_number: int
    current_number: int
    expected_number: int
    caption_text: str


@dataclass
class MalformedCaption:
    """
    A class to record a malformed caption (colon inside bolding).

    Attributes:
        file_path (Path): The path to the file.
        line_number (int): The line number (1-indexed for display).
        full_line (str): The full line content.
    """

    file_path: Path
    line_number: int
    full_line: str


def is_caption_line(line: str) -> bool:
    """
    Check if a line is a caption line in the format **Kuva #**: text.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line is a caption line, False otherwise.
    """
    return CAPTION_PATTERN.match(line.strip()) is not None


def parse_caption(line: str, line_number: int) -> Caption | None:
    """
    Parse a caption line and return a Caption object.

    Args:
        line (str): The line to parse.
        line_number (int): The line number (0-indexed).

    Returns:
        Caption | None: A Caption object if the line is a valid caption, None otherwise.
    """
    match = CAPTION_PATTERN.match(line.strip())
    if match:
        return Caption(
            line_number=line_number,
            current_number=int(match.group(1)),
            text=match.group(2),
            full_line=line,
        )
    return None


class CaptionFile:
    """
    A class to manage captions in a Markdown file.

    Attributes:
        file_path (Path): The path to the Markdown file.
        lines (list[str]): All lines in the file.
        captions (list[Caption]): List of captions found in the file.
    """

    def __init__(self, file_path: Path, auto_load: bool = True):
        self.file_path = file_path
        self.lines: list[str] = []
        self.captions: list[Caption] = []

        if auto_load:
            self._load_captions()

    def _load_captions(self):
        """
        Load captions from the Markdown file.
        """
        content = self.file_path.read_text(encoding="utf-8")
        self.lines = content.splitlines()

        for line_number, line in enumerate(self.lines):
            caption = parse_caption(line, line_number)
            if caption:
                self.captions.append(caption)

    def get_caption_issues(self) -> list[CaptionIssue]:
        """
        Get a list of caption numbering issues.

        Returns:
            list[CaptionIssue]: List of issues where caption numbers don't match expected order.
        """
        issues = []
        for expected_number, caption in enumerate(self.captions, start=1):
            if caption.current_number != expected_number:
                issues.append(
                    CaptionIssue(
                        file_path=self.file_path,
                        line_number=caption.line_number + 1,  # 1-indexed for display
                        current_number=caption.current_number,
                        expected_number=expected_number,
                        caption_text=caption.text[:50]
                        + ("..." if len(caption.text) > 50 else ""),
                    )
                )
        return issues

    def is_in_order(self) -> bool:
        """
        Check if all captions are in numerical order starting from 1.

        Returns:
            bool: True if captions are in order, False otherwise.
        """
        return len(self.get_caption_issues()) == 0

    def get_malformed_captions(self) -> list[MalformedCaption]:
        """
        Get a list of malformed captions where the colon is inside the bolding.

        Returns:
            list[MalformedCaption]: List of malformed captions found in the file.
        """
        malformed = []
        for line_number, line in enumerate(self.lines):
            if MALFORMED_CAPTION_PATTERN.search(line.strip()):
                malformed.append(
                    MalformedCaption(
                        file_path=self.file_path,
                        line_number=line_number + 1,  # 1-indexed for display
                        full_line=line.strip(),
                    )
                )
        return malformed

    def _get_fixed_content(self) -> str:
        """
        Get the file content with captions renumbered in order.

        Returns:
            str: The fixed content with captions renumbered.
        """
        fixed_lines = self.lines.copy()

        for expected_number, caption in enumerate(self.captions, start=1):
            if caption.current_number != expected_number:
                # Preserve leading whitespace from original line
                leading_whitespace = len(caption.full_line) - len(
                    caption.full_line.lstrip()
                )
                prefix = caption.full_line[:leading_whitespace]
                fixed_lines[caption.line_number] = (
                    prefix + caption.get_renumbered_line(expected_number)
                )

        return "\n".join(fixed_lines)

    def fix_captions(self) -> int:
        """
        Fix caption numbering in the file by renumbering them sequentially.

        Returns:
            int: The number of captions that were renumbered.
        """
        issues = self.get_caption_issues()
        if not issues:
            return 0

        fixed_content = self._get_fixed_content()
        self.file_path.write_text(fixed_content, encoding="utf-8")
        return len(issues)


def print_caption_status(caption_files: list[CaptionFile]):
    """
    Print the status of captions in all files.

    Args:
        caption_files (list[CaptionFile]): List of CaptionFile instances.
    """
    all_issues = []
    all_malformed = []
    files_ok = []

    for cf in caption_files:
        issues = cf.get_caption_issues()
        malformed = cf.get_malformed_captions()
        
        if issues:
            all_issues.extend(issues)
        
        if malformed:
            all_malformed.extend(malformed)
        
        if not issues and not malformed:
            files_ok.append(cf.file_path)

    # Print malformed caption warnings first
    if all_malformed:
        print("⚠️  WARNING: Malformed captions detected (colon inside bolding):")
        print(
            tabulate(
                [
                    {
                        "file_path": mal.file_path,
                        "line": mal.line_number,
                        "content": mal.full_line,
                    }
                    for mal in all_malformed
                ],
                headers="keys",
            )
        )
        print("")
        print("These captions will be ignored by auto-numbering.")
        print("Correct format: **Kuva #**: Caption text")
        print("Wrong format:   **Kuva #:**")
        print("")

    # Print files that are OK
    for file_path in files_ok:
        print(f"✅ {file_path}: Captions in order")

    # Print issues
    if all_issues:
        print("")
        print("Caption numbering issues:")
        print(
            tabulate(
                [
                    {
                        "file_path": issue.file_path,
                        "line": issue.line_number,
                        "current": issue.current_number,
                        "expected": issue.expected_number,
                        "caption": issue.caption_text,
                    }
                    for issue in all_issues
                ],
                headers="keys",
            )
        )
    elif not files_ok and not all_malformed:
        print("No captions found in the provided files.")
    elif not all_issues and files_ok and not all_malformed:
        print("")
        print("✅ All captions are in order.")


def fix_caption_files(caption_files: list[CaptionFile]):
    """
    Fix caption numbering in all files and print the results.

    Args:
        caption_files (list[CaptionFile]): List of CaptionFile instances.
    """
    for cf in caption_files:
        fixed_count = cf.fix_captions()
        if fixed_count > 0:
            print(f"🔧 {cf.file_path}: Fixed {fixed_count} caption(s)")
        else:
            print(f"✅ {cf.file_path}: No changes needed")
