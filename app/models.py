
from dataclasses import dataclass

@dataclass
class Record:
    rule_topic: str
    rule_text: str
    applies_to: str
    document_title: str
    page_or_section: str
    source_url: str
