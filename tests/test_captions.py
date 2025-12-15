import pytest
from pathlib import Path
from oat_tools.captions import (
    Caption,
    CaptionFile,
    CaptionIssue,
    MalformedCaption,
    is_caption_line,
    parse_caption,
)


class TestIsCaptionLine:
    """Tests for the is_caption_line function."""

    def test_valid_caption_line(self):
        assert is_caption_line("**Kuva 1**: Some caption text") is True

    def test_valid_caption_line_with_number(self):
        assert is_caption_line("**Kuva 42**: Another caption") is True

    def test_caption_line_with_leading_whitespace(self):
        assert is_caption_line("  **Kuva 1**: Caption with whitespace") is True

    def test_not_caption_line_plain_text(self):
        assert is_caption_line("This is just regular text") is False

    def test_not_caption_line_partial_match(self):
        assert is_caption_line("**Kuva**: Missing number") is False

    def test_not_caption_line_wrong_format(self):
        assert is_caption_line("Kuva 1: No asterisks") is False

    def test_empty_line(self):
        assert is_caption_line("") is False


class TestParseCaption:
    """Tests for the parse_caption function."""

    def test_parse_valid_caption(self):
        caption = parse_caption("**Kuva 1**: Test caption", 0)
        assert caption is not None
        assert caption.current_number == 1
        assert caption.text == "Test caption"
        assert caption.line_number == 0

    def test_parse_caption_with_larger_number(self):
        caption = parse_caption("**Kuva 123**: Large number caption", 5)
        assert caption is not None
        assert caption.current_number == 123
        assert caption.text == "Large number caption"
        assert caption.line_number == 5

    def test_parse_invalid_caption(self):
        caption = parse_caption("Not a caption line", 0)
        assert caption is None

    def test_parse_caption_with_special_characters(self):
        caption = parse_caption("**Kuva 1**: Caption with (special) characters!", 0)
        assert caption is not None
        assert caption.text == "Caption with (special) characters!"


class TestCaption:
    """Tests for the Caption dataclass."""

    def test_get_renumbered_line(self):
        caption = Caption(
            line_number=0,
            current_number=5,
            text="Some caption",
            full_line="**Kuva 5**: Some caption",
        )
        assert caption.get_renumbered_line(1) == "**Kuva 1**: Some caption"

    def test_get_renumbered_line_preserves_text(self):
        caption = Caption(
            line_number=0,
            current_number=10,
            text="Complex caption with numbers 123",
            full_line="**Kuva 10**: Complex caption with numbers 123",
        )
        assert (
            caption.get_renumbered_line(2)
            == "**Kuva 2**: Complex caption with numbers 123"
        )


class TestCaptionFile:
    """Tests for the CaptionFile class."""

    def test_load_captions_from_file(self, tmp_path):
        # Create a test file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Header\n\n**Kuva 1**: First caption\n\nSome text\n\n**Kuva 2**: Second caption\n"
        )

        cf = CaptionFile(test_file)
        assert len(cf.captions) == 2
        assert cf.captions[0].current_number == 1
        assert cf.captions[1].current_number == 2

    def test_captions_in_order(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("**Kuva 1**: First\n**Kuva 2**: Second\n**Kuva 3**: Third\n")

        cf = CaptionFile(test_file)
        assert cf.is_in_order() is True

    def test_captions_out_of_order(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("**Kuva 2**: First\n**Kuva 1**: Second\n**Kuva 5**: Third\n")

        cf = CaptionFile(test_file)
        assert cf.is_in_order() is False

    def test_get_caption_issues(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("**Kuva 3**: Should be 1\n**Kuva 5**: Should be 2\n")

        cf = CaptionFile(test_file)
        issues = cf.get_caption_issues()

        assert len(issues) == 2
        assert issues[0].current_number == 3
        assert issues[0].expected_number == 1
        assert issues[1].current_number == 5
        assert issues[1].expected_number == 2

    def test_no_caption_issues_when_correct(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("**Kuva 1**: First\n**Kuva 2**: Second\n")

        cf = CaptionFile(test_file)
        issues = cf.get_caption_issues()

        assert len(issues) == 0

    def test_fix_captions(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Header\n\n**Kuva 5**: First caption\n\nSome text\n\n**Kuva 10**: Second caption\n"
        )

        cf = CaptionFile(test_file)
        fixed_count = cf.fix_captions()

        assert fixed_count == 2

        # Read the file again and verify
        content = test_file.read_text()
        assert "**Kuva 1**: First caption" in content
        assert "**Kuva 2**: Second caption" in content
        assert "**Kuva 5**" not in content
        assert "**Kuva 10**" not in content

    def test_fix_captions_no_changes_needed(self, tmp_path):
        test_file = tmp_path / "test.md"
        original_content = "**Kuva 1**: First\n**Kuva 2**: Second\n"
        test_file.write_text(original_content)

        cf = CaptionFile(test_file)
        fixed_count = cf.fix_captions()

        assert fixed_count == 0
        assert test_file.read_text() == original_content

    def test_fix_captions_preserves_other_content(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Title\n\nParagraph text here.\n\n**Kuva 99**: Caption\n\n## Another section\n\nMore text.\n"
        )

        cf = CaptionFile(test_file)
        cf.fix_captions()

        content = test_file.read_text()
        assert "# Title" in content
        assert "Paragraph text here." in content
        assert "**Kuva 1**: Caption" in content
        assert "## Another section" in content
        assert "More text." in content

    def test_file_with_no_captions(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("# Just a header\n\nSome text without captions.\n")

        cf = CaptionFile(test_file)
        assert len(cf.captions) == 0
        assert cf.is_in_order() is True
        assert cf.get_caption_issues() == []


class TestMalformedCaptions:
    """Tests for malformed caption detection."""

    def test_detect_single_malformed_caption(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("**Kuva 1:**\n\nSome text here.\n")

        cf = CaptionFile(test_file)
        malformed = cf.get_malformed_captions()

        assert len(malformed) == 1
        assert malformed[0].line_number == 1
        assert "**Kuva 1:**" in malformed[0].full_line

    def test_detect_multiple_malformed_captions(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "**Kuva 1:**\n\nSome text\n\n**Kuva 2:**\n\nMore text\n"
        )

        cf = CaptionFile(test_file)
        malformed = cf.get_malformed_captions()

        assert len(malformed) == 2
        assert malformed[0].line_number == 1
        assert malformed[1].line_number == 5

    def test_no_malformed_captions_when_correct_format(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "**Kuva 1**: First caption\n\n**Kuva 2**: Second caption\n"
        )

        cf = CaptionFile(test_file)
        malformed = cf.get_malformed_captions()

        assert len(malformed) == 0

    def test_malformed_caption_with_leading_whitespace(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text("  **Kuva 1:**\n\nSome text\n")

        cf = CaptionFile(test_file)
        malformed = cf.get_malformed_captions()

        assert len(malformed) == 1
        assert malformed[0].line_number == 1

    def test_mixed_correct_and_malformed_captions(self, tmp_path):
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "**Kuva 1**: Correct caption\n\n**Kuva 2:**\n\n**Kuva 3**: Another correct\n"
        )

        cf = CaptionFile(test_file)
        malformed = cf.get_malformed_captions()

        # Only one malformed caption
        assert len(malformed) == 1
        assert malformed[0].line_number == 3

        # But only 2 valid captions are parsed
        assert len(cf.captions) == 2
