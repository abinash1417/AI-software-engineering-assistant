from dataclasses import dataclass
from typing import TypedDict


@dataclass
class CodeSubmission:
    """Represents a piece of code submitted for review."""
    code: str
    language: str

    def is_valid(self) -> bool:
        return bool(self.code and self.code.strip())

    def char_count(self) -> int:
        return len(self.code)


class ReviewState(TypedDict):
    """Shared state passed between nodes in the review pipeline graph."""
    code: str
    language: str
    analysis: str
    issues: str
    tests: str
    report_raw: str
    report: dict