import math
import re

from dataclasses import dataclass, field

def extract_id(full_reference_line: str) -> str:
        """
        Extract a valid reference ID from the full reference line.
        """
        words = full_reference_line.split()
        if not words:
            raise ValueError("The reference line is empty or does not contain a valid ID.")
        
        first_word = words[0]
        
        # Use regex to match the Vancouver style reference ID
        match = re.match(r'^\[\^([\w-]+)\]:', first_word)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Invalid reference ID format: {first_word}. Expected format is [^id]:")

def is_reference_line(line: str) -> bool:
    """
    Identify if a line in a Markdown file is a Vancouver style reference line.
    Args:
        line (str): The line to check.
    Returns:
        bool: True if the line is a reference line, False otherwise.
    Raises:
        ValueError: If the line is a reference line but does not contain any text after the ID.
    """
    
    words = line.split()
    if not words:
        return False
    
    first_word = words[0]
    rest = words[1:]
    
    if len(rest) == 0 and first_word.startswith('[^') and first_word.endswith(']:'):
        raise ValueError(f"A line with reference {first_word} does not contain any text after the ID.")

    if first_word.startswith('[^') and first_word.endswith(']:'):
        return True
    return False

@dataclass
class Reference:
    """
    A class that represents a Vancouver style reference in a Markdown file.

    Attributes:
        full_reference_line (str): The full reference line as it appears in the Markdown file.
        first_appearance_pos (int | None): The character position where the reference first appears.
        number_of_appearances (int): The number of times the reference appears in the file.
    """
    full_reference_line: str
    first_appearance_pos: int | None = None
    number_of_appearances: int = 0

    def __post_init__(self):
        self.reference_id = extract_id(self.full_reference_line)

    def record_appearance(self, position: int):
        if self.first_appearance_pos is None:
            self.first_appearance_pos = position
        elif self.first_appearance_pos > position:
            self.first_appearance_pos = position
        else:
            pass

        self.number_of_appearances += 1


@dataclass
class ReferenceCollection:
    """
    A class that represents the Vancouver style references in a given Markdown file.

    Attributes:
        references (list[Reference]): A list of Reference objects representing the references in the file.

    Methods:
        add_reference(full_reference_line: str): Add a new reference to the collection.
        get_reference_by_id(reference_id: str): Get a reference by its ID.
        get_unappearing_references(): Get references that do not appear in the body text.
        get_ordered_by_pos(only_appearing=False): Get the references ordered by their first appearance position.

    Raises:
        ValueError: If a reference with the same ID already exists or if a reference line is invalid.
    """
    references: list[Reference] = field(default_factory=list)

    def add_reference(self, full_reference_line: str):
        """
        Add a new reference to the collection.
        """
        reference_id = extract_id(full_reference_line)
        
        # Check if reference already exists by iterating through references
        for ref in self.references:
            if ref.reference_id == reference_id:
                raise ValueError(f"Reference with ID {reference_id} already exists.")
        
        reference = Reference(full_reference_line)
        self.references.append(reference)

    def get_reference_by_id(self, reference_id: str) -> Reference:
        """
        Get a reference by its ID.
        """
        for ref in self.references:
            if ref.reference_id == reference_id:
                return ref
        raise ValueError(f"Reference with ID {reference_id} not found. Existing references: {[r.reference_id for r in self.references]}")
    
    def get_unappearing_references(self) -> list[Reference]:
        """
        Get references that do not appear in the body text.
        """
        return [ref for ref in self.references if ref.number_of_appearances == 0]
    
    def get_ordered_by_pos(self, only_appearing=False) -> list[Reference]:
        """
        Get the references ordered by their first appearance position.
        """
        references = sorted(self.references, key=lambda ref: ref.first_appearance_pos or math.inf)
        if only_appearing:
            references = [ref for ref in references if ref.number_of_appearances > 0]
        return references
