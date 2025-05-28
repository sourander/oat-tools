import tempfile
from pathlib import Path

from oat_tools.wordcounter import count_words
from textwrap import dedent


class TestCountWords:
    """Test cases for the count_words function."""

    def test_basic_word_counting(self):
        """Test basic word counting functionality."""
        content = "This is a simple test with seven words."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            assert result == 8  # "This", "is", "a", "simple", "test", "with", "seven", "words"

    def test_empty_file(self):
        """Test counting words in an empty file."""
        content = ""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            assert result == 0

    def test_whitespace_only(self):
        """Test counting words in a file with only whitespace."""
        content = "   \n\t  \n  "
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            assert result == 0

    def test_exclude_code_blocks(self):
        """Test that code blocks are excluded from word count."""
        content = dedent("""
            This is regular text with five words.

            ```python
            def hello():
                print("This code should not be counted")
                return "neither should this"
            ```

            And this is more regular text with seven words.
            """).strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            # Should count: "This", "is", "regular", "text", "with", "five", "words", 
            # "And", "this", "is", "more", "regular", "text", "with", "seven", "words"
            assert result == 16

    def test_exclude_multiple_code_blocks(self):
        """Test that multiple code blocks are excluded."""
        content = dedent("""
            Start with three words.

            ```bash
            echo "first code block"
            ```

            Middle has two words.

            ```javascript
            console.log("second code block");
            ```

            End with two words.
            """).strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            # Should count: "Start", "with", "three", "words", "Middle", "has", "two", "words", "End", "with", "two", "words"
            assert result == 12

    def test_exclude_footnotes(self):
        """Test that footnotes are excluded from word count."""
        content = dedent("""
            This text references something [^1] and another thing [^2].

            [^1]: This is a footnote that should not be counted
            [^2]: Another footnote with several words that should also be ignored

            Regular text continues here with more words.
            """).strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            # Should count: "This", "text", "references", "something", "1", "and", "another", "thing", "2",
            # "Regular", "text", "continues", "here", "with", "more", "words"
            assert result == 16

    def test_exclude_urls(self):
        """Test that URLs are excluded from word count."""
        content = dedent("""
            Check out this website https://example.com for more info.
            Also visit http://another-site.org and https://github.com/user/repo.
            This text has five normal words.
            """).strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            # Should count: "Check", "out", "this", "website", "for", "more", "info",
            # "Also", "visit", "and", "This", "text", "has", "five", "normal", "words"
            assert result == 16

    def test_markdown_headers_and_formatting(self):
        """Test that markdown headers and formatting are counted correctly."""
        content = dedent("""
            # Header One
            ## Header Two
            ### Header Three

            **Bold text** and *italic text* and `inline code`.

            - List item one
            - List item two
            - List item three

            > This is a blockquote with several words.
            """).strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            result = count_words(Path(f.name))
            # Should count all visible text including headers, bold, italic, but excluding inline code formatting
            # "Header", "One", "Header", "Two", "Header", "Three", "Bold", "text", "and", "italic", "text", "and", "inline", "code",
            # "List", "item", "one", "List", "item", "two", "List", "item", "three", "This", "is", "a", "blockquote", "with", "several", "words"
            assert result == 30

    # def test_existing_test_file(self):
    #     """Test using the existing test data file."""
    #     test_file = Path("tests/data/testing.md")
    #     result = count_words(test_file)
    #     assert result == 6

    # def test_empty_test_file(self):
    #     """Test using the empty test data file."""
    #     test_file = Path("tests/data/another.md")
    #     result = count_words(test_file)
    #     assert result == 0

