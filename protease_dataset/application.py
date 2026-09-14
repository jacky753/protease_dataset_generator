from __future__ import annotations

from dataclasses import dataclass

from .config import AppConfig
from .ports import CleavageSiteRepository, DatasetResultWriter
from .services.negative_dataset import NegativeDatasetService
from .services.positive_dataset import PositiveDatasetService


@dataclass(frozen=True)
class RunSummary:
    protease: str
    substrate_sites: int
    positive_records: int
    negative_records: int
    positive_short_sequences: int
    negative_short_sequences: int
    id_errors: int
    no_negative_data: int


class DatasetApplication:
    """Coordinates use cases without knowing MySQL, HTTP, or CSV implementation details."""

    def __init__(
        self,
        config: AppConfig,
        cleavage_repository: CleavageSiteRepository,
        positive_service: PositiveDatasetService,
        negative_service: NegativeDatasetService,
        writer: DatasetResultWriter,
    ) -> None:
        self._config = config
        self._repository = cleavage_repository
        self._positive_service = positive_service
        self._negative_service = negative_service
        self._writer = writer

    def run(self) -> RunSummary:
        protease = self._config.target_protease
        sites = tuple(self._repository.get_by_protease(protease))
        if not sites:
            raise RuntimeError(f"No cleavage sites found for {protease}")

        positive = self._positive_service.generate(
            protease,
            self._config.protease_turn,
            sites,
        )
        negative = self._negative_service.generate(
            protease,
            self._config.protease_turn,
            sites,
        )

        self._writer.write_positive(protease, positive)
        self._writer.write_negative(protease, negative)

        return RunSummary(
            protease=protease,
            substrate_sites=len(sites),
            positive_records=len(positive.records),
            negative_records=len(negative.records),
            positive_short_sequences=len(positive.short_sequences),
            negative_short_sequences=len(negative.short_sequences),
            id_errors=len(positive.id_errors) + len(negative.id_errors),
            no_negative_data=len(negative.no_negative_data),
        )

    def close(self) -> None:
        self._repository.close()
