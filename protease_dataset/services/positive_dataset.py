from __future__ import annotations

from collections.abc import Sequence

from ..domain import (
    CleavageSite,
    PositiveDatasetResult,
    PositiveRecord,
    ShortSequenceRecord,
    UniProtIdErrorRecord,
)
from ..ports import ProteinSequenceProvider
from .sequence_processing import SequenceWindowExtractor
from .uniprot_id import InvalidUniProtIdError, UniProtIdNormalizer


class PositiveDatasetService:
    """Generates positive cleavage windows only; persistence is handled elsewhere."""

    def __init__(
        self,
        sequence_provider: ProteinSequenceProvider,
        id_normalizer: UniProtIdNormalizer,
        extractor: SequenceWindowExtractor,
    ) -> None:
        self._sequence_provider = sequence_provider
        self._id_normalizer = id_normalizer
        self._extractor = extractor

    def generate(
        self,
        protease: str,
        protease_turn: int,
        sites: Sequence[CleavageSite],
    ) -> PositiveDatasetResult:
        result = PositiveDatasetResult()

        for substrate_turn, site in enumerate(sites):
            try:
                uniprot_id = self._id_normalizer.normalize(site.uniprot_id)
            except InvalidUniProtIdError:
                result.id_errors.append(
                    UniProtIdErrorRecord(
                        protease_turn,
                        protease,
                        substrate_turn,
                        site.uniprot_id,
                    )
                )
                continue

            full_aa = self._sequence_provider.get_sequence(uniprot_id)
            if len(full_aa) < self._extractor.trim_len:
                result.short_sequences.append(
                    ShortSequenceRecord(
                        protease_turn,
                        protease,
                        substrate_turn,
                        uniprot_id,
                        full_aa,
                        len(full_aa),
                        site.p1,
                    )
                )
                continue

            result.records.append(
                PositiveRecord(
                    protease_turn=protease_turn,
                    merops_id=protease,
                    substrate_turn=substrate_turn,
                    uniprot_id=uniprot_id,
                    p1=site.p1,
                    len_full_aa=len(full_aa),
                    cleave_pattern=self._extractor.positive_window(full_aa, site.p1),
                    full_aa=full_aa,
                )
            )

        return result
