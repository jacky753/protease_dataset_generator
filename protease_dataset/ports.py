from __future__ import annotations

from typing import Protocol, Sequence

from .domain import CleavageSite, NegativeDatasetResult, PositiveDatasetResult


class CleavageSiteRepository(Protocol):
    """Abstraction for obtaining known cleavage sites."""

    def get_by_protease(self, protease_code: str) -> Sequence[CleavageSite]:
        ...

    def close(self) -> None:
        ...


class ProteinSequenceProvider(Protocol):
    """Abstraction for obtaining a full amino-acid sequence."""

    def get_sequence(self, uniprot_id: str) -> str:
        ...


class DatasetResultWriter(Protocol):
    """Abstraction for persistence of generated datasets."""

    def write_positive(self, protease: str, result: PositiveDatasetResult) -> None:
        ...

    def write_negative(self, protease: str, result: NegativeDatasetResult) -> None:
        ...
