from __future__ import annotations

import re


class InvalidUniProtIdError(ValueError):
    pass


class UniProtIdNormalizer:
    """Normalizes legacy substrate IDs to the first valid six-character accession token."""

    _exact = re.compile(r"^[A-Z0-9]{6}$")
    _prefix = re.compile(r"^([A-Z0-9]{6})")

    def normalize(self, raw_id: str) -> str:
        value = raw_id.strip().upper()
        if self._exact.fullmatch(value):
            return value

        match = self._prefix.match(value)
        if match:
            return match.group(1)

        raise InvalidUniProtIdError(f"Invalid UniProt ID: {raw_id!r}")
