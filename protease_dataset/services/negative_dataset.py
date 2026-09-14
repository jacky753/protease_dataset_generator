from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence

import numpy as np

from ..domain import (
    CleavageSite,
    NegativeDatasetResult,
    NegativeRecord,
    NoNegativeDataRecord,
    ShortSequenceRecord,
    UniProtIdErrorRecord,
)
from ..ports import ProteinSequenceProvider
from .sequence_processing import SequenceWindowExtractor
from .uniprot_id import InvalidUniProtIdError, UniProtIdNormalizer


class NegativeDatasetService:
    """Generates negatives outside all known cleavage windows for each protein."""

    def __init__(
        self,
        sequence_provider: ProteinSequenceProvider,
        id_normalizer: UniProtIdNormalizer,
        extractor: SequenceWindowExtractor,
        random_seed: int = 42,
    ) -> None:
        self._sequence_provider = sequence_provider
        self._id_normalizer = id_normalizer
        self._extractor = extractor
        self._random_seed = random_seed

    def generate(
        self,
        protease: str,
        protease_turn: int,
        sites: Sequence[CleavageSite],
    ) -> NegativeDatasetResult:
        result = NegativeDatasetResult()
        rng = np.random.RandomState(self._random_seed)

        grouped: "OrderedDict[str, list[tuple[int, CleavageSite]]]" = OrderedDict()
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
            grouped.setdefault(uniprot_id, []).append((substrate_turn, site))

        for uniprot_id, indexed_sites in grouped.items():
            first_substrate_turn, first_site = indexed_sites[0]
            full_aa = self._sequence_provider.get_sequence(uniprot_id)

            if len(full_aa) < self._extractor.trim_len:
                result.short_sequences.append(
                    ShortSequenceRecord(
                        protease_turn,
                        protease,
                        first_substrate_turn,
                        uniprot_id,
                        full_aa,
                        len(full_aa),
                        first_site.p1,
                    )
                )
                continue

            p1_values = [site.p1 for _, site in indexed_sites]
            safe_ranges = self._extractor.safe_ranges(len(full_aa), p1_values)
            eligible_ranges = [
                (start, end)
                for start, end in safe_ranges
                if end - start + 1 >= self._extractor.trim_len
            ]
            result.candidate_ranges.extend(
                (uniprot_id, start, end) for start, end in eligible_ranges
            )

            if not eligible_ranges:
                result.no_negative_data.append(
                    NoNegativeDataRecord(
                        protease_turn,
                        protease,
                        first_substrate_turn,
                        uniprot_id,
                        full_aa,
                        len(full_aa),
                    )
                )
                continue

            samples = self._extractor.sample_windows_from_ranges(
                full_aa,
                eligible_ranges,
                rng,
            )
            for window, range_start, range_end, sample_start in samples:
                result.records.append(
                    NegativeRecord(
                        protease_turn=protease_turn,
                        merops_id=protease,
                        substrate_turn=first_substrate_turn,
                        uniprot_id=uniprot_id,
                        # p1 is retained for CSV compatibility. For proteins with
                        # multiple sites it stores the first known p1; all p1 values
                        # are nevertheless excluded when generating negatives.
                        p1=first_site.p1,
                        negative_pattern=window,
                        full_aa=full_aa,
                        len_full_aa=len(full_aa),
                        start=range_start,
                        end=range_end,
                        sample_start=sample_start,
                    )
                )

        return result
