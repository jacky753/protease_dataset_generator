from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class CleavageSite:
    """A known cleavage site for one substrate protein."""

    uniprot_id: str
    p1: int


@dataclass(frozen=True)
class PositiveRecord:
    protease_turn: int
    merops_id: str
    substrate_turn: int
    uniprot_id: str
    p1: int
    len_full_aa: int
    cleave_pattern: str
    full_aa: str


@dataclass(frozen=True)
class NegativeRecord:
    protease_turn: int
    merops_id: str
    substrate_turn: int
    uniprot_id: str
    p1: int
    negative_pattern: str
    full_aa: str
    len_full_aa: int
    start: int
    end: int
    sample_start: int


@dataclass(frozen=True)
class ShortSequenceRecord:
    protease_num: int
    merops_id: str
    substrate_num: int
    uniprot_id: str
    full_aa: str
    full_aa_length: int
    p1: int


@dataclass(frozen=True)
class UniProtIdErrorRecord:
    protease_turn: int
    merops_id: str
    substrate_turn: int
    uniprot_id: str


@dataclass(frozen=True)
class NoNegativeDataRecord:
    protease_turn: int
    merops_id: str
    substrate_turn: int
    uniprot_id: str
    full_aa: str
    full_aa_length: int


@dataclass
class PositiveDatasetResult:
    records: list[PositiveRecord] = field(default_factory=list)
    short_sequences: list[ShortSequenceRecord] = field(default_factory=list)
    id_errors: list[UniProtIdErrorRecord] = field(default_factory=list)


@dataclass
class NegativeDatasetResult:
    records: list[NegativeRecord] = field(default_factory=list)
    short_sequences: list[ShortSequenceRecord] = field(default_factory=list)
    id_errors: list[UniProtIdErrorRecord] = field(default_factory=list)
    no_negative_data: list[NoNegativeDataRecord] = field(default_factory=list)
    candidate_ranges: list[tuple[str, int, int]] = field(default_factory=list)


SubstrateCollection = Sequence[CleavageSite]
