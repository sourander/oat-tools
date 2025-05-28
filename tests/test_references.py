import pytest

from oat_tools.references import ReferenceCollection, Reference, extract_id, is_reference_line


class TestExtractId:
    """Test the extract_id function."""
    
    def test_extract_id_valid_reference(self):
        """Test extracting ID from a valid Vancouver style reference."""
        assert extract_id("[^1]: Author, A. (2023). Title. Journal.") == "1"
        assert extract_id("[^ref1]: Smith, J. (2024). Research paper.") == "ref1"
        assert extract_id("[^my-ref]: Doe, J. et al. (2022). Study.") == "my-ref"
    
    def test_extract_id_empty_line(self):
        """Test that empty lines raise ValueError."""
        with pytest.raises(ValueError, match="The reference line is empty"):
            extract_id("")
        with pytest.raises(ValueError, match="The reference line is empty"):
            extract_id("   ")
    
    def test_extract_id_invalid_format(self):
        """Test that invalid reference formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("1: Invalid format")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[1]: Missing caret")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[^1] Missing colon")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[^this contains a whitespace]:")


class TestIsReferenceLine:
    """Test the is_reference_line function."""
    
    def test_valid_reference_lines(self):
        """Test that valid reference lines are identified correctly."""
        assert is_reference_line("[^1]: Author, A. (2023). Title.")
        assert is_reference_line("[^ref1]: Smith, J. (2024). Research.")
        assert is_reference_line("[^my-ref]: Doe, J. et al. (2022). Study.")
        assert is_reference_line("[^complex-id_123]: Complex reference with ID.")
    
    def test_invalid_reference_lines(self):
        """Test that non-reference lines return False."""
        assert not is_reference_line("This is just normal text")
        assert not is_reference_line("# Heading")
        assert not is_reference_line("Some text with [^1] citation")
        assert not is_reference_line("")
        assert not is_reference_line("[^complex id 123]: Complex reference with ID.")
    
    def test_reference_line_without_text(self):
        """Test that reference lines without text after ID raise ValueError."""
        with pytest.raises(ValueError):
            is_reference_line("[^1]:")
        with pytest.raises(ValueError):
            is_reference_line("[^ref]:")


class TestReference:
    """Test the Reference class."""
    
    def test_reference_creation(self):
        """Test creating a Reference object."""
        ref = Reference("[^1]: Author, A. (2023). Title of paper.")
        assert ref.full_reference_line == "[^1]: Author, A. (2023). Title of paper."
        assert ref.reference_id == "1"
        assert ref.first_appearance_pos is None
        assert ref.number_of_appearances == 0
    
    def test_reference_creation_with_complex_id(self):
        """Test creating a Reference with complex ID."""
        ref = Reference("[^my-ref-123]: Complex reference.")
        assert ref.reference_id == "my-ref-123"
    
    def test_reference_invalid_format(self):
        """Test that invalid reference format raises ValueError."""
        with pytest.raises(ValueError):
            Reference("Invalid reference format")
    
    def test_record_appearance_first_time(self):
        """Test recording the first appearance of a reference."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)
        
        assert ref.first_appearance_pos == 100
        assert ref.number_of_appearances == 1
    
    def test_record_appearance_multiple_times(self):
        """Test recording multiple appearances."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)
        ref.record_appearance(200)
        ref.record_appearance(50)  # Earlier position
        
        assert ref.first_appearance_pos == 50  # Should be the earliest position
        assert ref.number_of_appearances == 3
    
    def test_record_appearance_same_position(self):
        """Test recording appearance at the same position multiple times."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)
        ref.record_appearance(100)
        
        assert ref.first_appearance_pos == 100
        assert ref.number_of_appearances == 2


class TestReferenceCollection:
    """Test the ReferenceCollection class."""
    
    def test_empty_collection(self):
        """Test creating an empty reference collection."""
        collection = ReferenceCollection()
        assert len(collection.references) == 0
        assert collection.get_unappearing_references() == []
        assert collection.get_ordered_by_pos() == []
    
    def test_add_reference(self):
        """Test adding a reference to the collection."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        
        assert len(collection.references) == 1
        assert collection.references[0].reference_id == "1"
        assert collection.references[0].full_reference_line == "[^1]: First reference."
    
    def test_add_multiple_references(self):
        """Test adding multiple references."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^ref3]: Third reference.")
        
        assert len(collection.references) == 3
        ids = [ref.reference_id for ref in collection.references]
        assert "1" in ids
        assert "2" in ids
        assert "ref3" in ids
    
    def test_add_duplicate_reference(self):
        """Test that adding duplicate reference raises ValueError."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        
        with pytest.raises(ValueError, match="Reference with ID 1 already exists"):
            collection.add_reference("[^1]: Duplicate reference.")
    
    def test_get_reference_by_id(self):
        """Test retrieving a reference by its ID."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^test]: Test reference.")
        
        ref1 = collection.get_reference_by_id("1")
        assert ref1 is not None
        assert ref1.reference_id == "1"
        assert ref1.full_reference_line == "[^1]: First reference."
        
        ref_test = collection.get_reference_by_id("test")
        assert ref_test is not None
        assert ref_test.reference_id == "test"
    
    def test_get_reference_by_id_nonexistent(self):
        """Test that getting a nonexistent reference raises ValueError."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        
        with pytest.raises(ValueError, match="Reference with ID nonexistent not found"):
            collection.get_reference_by_id("nonexistent")
    
    def test_get_unappearing_references(self):
        """Test getting references that don't appear in text."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: Used reference.")
        collection.add_reference("[^2]: Unused reference.")
        collection.add_reference("[^3]: Another unused reference.")
        
        # Mark one reference as appearing
        ref1 = collection.get_reference_by_id("1")
        assert isinstance(ref1, Reference)
        ref1.record_appearance(100)
        
        unused = collection.get_unappearing_references()
        assert len(unused) == 2
        unused_ids = [ref.reference_id for ref in unused]
        assert "2" in unused_ids
        assert "3" in unused_ids
        assert "1" not in unused_ids
    
    def test_get_ordered_by_pos(self):
        """Test getting references ordered by first appearance position."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^3]: Third reference.")
        
        # Record appearances in different order
        collection.get_reference_by_id("2").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(200)
        collection.get_reference_by_id("3").record_appearance(100)
        
        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 3
        assert ordered[0].reference_id == "2"  # Position 50
        assert ordered[1].reference_id == "3"  # Position 100
        assert ordered[2].reference_id == "1"  # Position 200
    
    def test_get_ordered_by_pos_with_unappearing(self):
        """Test ordering when some references don't appear in text."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: Appearing reference.")
        collection.add_reference("[^2]: Non-appearing reference.")
        collection.add_reference("[^3]: Another appearing reference.")
        
        # Only record appearances for some references
        collection.get_reference_by_id("3").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(100)
        # ref2 has no appearances
        
        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 3
        assert ordered[0].reference_id == "3"  # Position 50
        assert ordered[1].reference_id == "1"  # Position 100
        assert ordered[2].reference_id == "2"  # No position (math.inf)
    
    def test_get_ordered_by_pos_only_appearing(self):
        """Test get_ordered_by_pos with only_appearing=True filters out non-appearing references."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^3]: Third reference.")
        collection.add_reference("[^4]: Fourth reference.")
        
        # Record appearances for only some references
        collection.get_reference_by_id("3").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(100)
        collection.get_reference_by_id("4").record_appearance(25)
        # ref2 has no appearances (number_of_appearances == 0)
        
        # Test with only_appearing=False (default behavior)
        all_ordered = collection.get_ordered_by_pos(only_appearing=False)
        assert len(all_ordered) == 4
        assert all_ordered[0].reference_id == "4"  # Position 25
        assert all_ordered[1].reference_id == "3"  # Position 50
        assert all_ordered[2].reference_id == "1"  # Position 100
        assert all_ordered[3].reference_id == "2"  # No position (math.inf)
        
        # Test with only_appearing=True (should exclude ref2)
        appearing_only = collection.get_ordered_by_pos(only_appearing=True)
        assert len(appearing_only) == 3
        assert appearing_only[0].reference_id == "4"  # Position 25
        assert appearing_only[1].reference_id == "3"  # Position 50
        assert appearing_only[2].reference_id == "1"  # Position 100
        # ref2 should not be in the list since it has number_of_appearances == 0
        
        # Verify that ref2 is not in the appearing_only list
        appearing_ids = [ref.reference_id for ref in appearing_only]
        assert "2" not in appearing_ids

    def test_integration_scenario(self):
        """Test a complete scenario simulating typical usage."""
        collection = ReferenceCollection()
        
        # Add references as they would be found in a markdown file
        collection.add_reference("[^1]: Smith, J. (2023). Research on AI. Journal of AI, 15(3), 123-145.")
        collection.add_reference("[^doe2024]: Doe, J. et al. (2024). Machine Learning Advances. Tech Review.")
        collection.add_reference("[^unused]: Unused reference that should be removed.")
        collection.add_reference("[^brown]: Brown, A. (2022). Data Science Methods. Data Journal.")
        
        # Simulate finding citations in the text (in order of appearance)
        collection.get_reference_by_id("doe2024").record_appearance(500)  # Second citation in text
        collection.get_reference_by_id("1").record_appearance(200)        # First citation in text
        collection.get_reference_by_id("brown").record_appearance(800)    # Third citation in text
        collection.get_reference_by_id("doe2024").record_appearance(1200) # Cited again later
        
        # Test getting unused references
        unused = collection.get_unappearing_references()
        assert len(unused) == 1
        assert unused[0].reference_id == "unused"
        
        # Test getting references ordered by appearance
        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 4
        assert ordered[0].reference_id == "1"       # Position 200
        assert ordered[1].reference_id == "doe2024" # Position 500
        assert ordered[2].reference_id == "brown"   # Position 800
        assert ordered[3].reference_id == "unused"  # No position (last)
        
        # Test appearance counts
        assert collection.get_reference_by_id("1").number_of_appearances == 1
        assert collection.get_reference_by_id("doe2024").number_of_appearances == 2
        assert collection.get_reference_by_id("brown").number_of_appearances == 1
        assert collection.get_reference_by_id("unused").number_of_appearances == 0

