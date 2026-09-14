from __future__ import annotations

from ..ports import ProteinSequenceProvider


class CachingProteinSequenceProvider:
    """In-memory decorator that avoids repeated HTTP fetches for the same accession."""

    def __init__(self, inner: ProteinSequenceProvider) -> None:
        self._inner = inner
        self._cache: dict[str, str] = {}

    def get_sequence(self, uniprot_id: str) -> str:
        if uniprot_id not in self._cache:
            self._cache[uniprot_id] = self._inner.get_sequence(uniprot_id)
        return self._cache[uniprot_id]
