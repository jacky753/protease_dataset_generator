from __future__ import annotations

from .application import DatasetApplication
from .config import AppConfig
from .infrastructure.cached_sequence_provider import CachingProteinSequenceProvider
from .infrastructure.csv_writer import CsvDatasetWriter
from .infrastructure.mysql_repository import MySqlCleavageSiteRepository
from .infrastructure.static_repository import StaticCleavageSiteRepository
from .infrastructure.uniprot_client import UniProtRestSequenceProvider
from .services.negative_dataset import NegativeDatasetService
from .services.positive_dataset import PositiveDatasetService
from .services.sequence_processing import SequenceWindowExtractor
from .services.uniprot_id import UniProtIdNormalizer


def build_application(config: AppConfig) -> DatasetApplication:
    config.validate()

    if config.substrate_source == "mysql":
        repository = MySqlCleavageSiteRepository(config.database)
    else:
        repository = StaticCleavageSiteRepository()

    sequence_provider = CachingProteinSequenceProvider(
        UniProtRestSequenceProvider(config.request_timeout_sec)
    )
    normalizer = UniProtIdNormalizer()
    extractor = SequenceWindowExtractor(config.trim_len)

    positive_service = PositiveDatasetService(
        sequence_provider,
        normalizer,
        extractor,
    )
    negative_service = NegativeDatasetService(
        sequence_provider,
        normalizer,
        extractor,
        random_seed=config.random_seed,
    )
    writer = CsvDatasetWriter(config.output_dir, config.chunk_size)

    return DatasetApplication(
        config,
        repository,
        positive_service,
        negative_service,
        writer,
    )
