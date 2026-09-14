from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable, TypeVar

import pandas as pd

from ..domain import NegativeDatasetResult, PositiveDatasetResult


T = TypeVar("T")

POSITIVE_COLUMNS = [
    "protease_turn",
    "merops_id",
    "substrate_turn",
    "uniprot_id",
    "p1",
    "len_full_aa",
    "cleave_pattern",
    "full_aa",
]
NEGATIVE_COLUMNS = [
    "protease_turn",
    "merops_id",
    "substrate_turn",
    "uniprot_id",
    "p1",
    "negative_pattern",
    "full_aa",
    "len_full_aa",
    "start",
    "end",
    "a[k]",
]
SHORT_SEQUENCE_COLUMNS = [
    "protease_num",
    "merops_id",
    "substrate_num",
    "uniprot_id",
    "full_aa",
    "full_aa_length",
    "p1",
]
ID_ERROR_COLUMNS = [
    "protease_turn",
    "merops_id",
    "substrate_turn",
    "uniprot_id",
]
NO_NEGATIVE_COLUMNS = [
    "protease_turn",
    "merops_id",
    "substrate_turn",
    "uniprot_id",
    "full_aa",
    "full_aa_length",
]


class CsvDatasetWriter:
    """CSV persistence only; generation logic does not depend on pandas or filenames."""

    def __init__(self, output_dir: Path, chunk_size: int = 500) -> None:
        self._output_dir = output_dir
        self._chunk_size = chunk_size
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def write_positive(self, protease: str, result: PositiveDatasetResult) -> None:
        self._write_chunks(
            result.records,
            f"cleave_pattern_one_letter_aa_{protease}_{{chunk}}.csv",
            POSITIVE_COLUMNS,
        )
        self._write_records(
            result.short_sequences,
            f"positive_pattern_aa_less_than_eight_{protease}.csv",
            SHORT_SEQUENCE_COLUMNS,
        )
        self._write_records(
            result.id_errors,
            f"positive_pattern_uniprot_id_error_{protease}.csv",
            ID_ERROR_COLUMNS,
        )

    def write_negative(self, protease: str, result: NegativeDatasetResult) -> None:
        self._write_chunks(
            result.records,
            f"negative_pattern_one_letter_aa_{protease}_{{chunk}}.csv",
            NEGATIVE_COLUMNS,
        )
        # Compatibility output used by the original script.
        self._write_records(
            result.records,
            f"negative_pattern_one_letter_aa_{protease}.csv",
            NEGATIVE_COLUMNS,
        )
        self._write_records(
            result.short_sequences,
            f"negative_pattern_aa_shorter_than_trim_len_{protease}.csv",
            SHORT_SEQUENCE_COLUMNS,
        )
        self._write_records(
            result.id_errors,
            f"negative_pattern_uniprot_id_error_{protease}.csv",
            ID_ERROR_COLUMNS,
        )
        self._write_records(
            result.no_negative_data,
            "df_no_nagative_data.csv",
            NO_NEGATIVE_COLUMNS,
        )
        self._write_candidate_ranges(protease, result.candidate_ranges)

    def _write_chunks(
        self,
        records: list[T],
        filename_pattern: str,
        columns: list[str],
    ) -> None:
        if not records:
            self._write_dataframe(
                pd.DataFrame(columns=columns),
                filename_pattern.format(chunk=0),
            )
            return

        for chunk_number, start in enumerate(range(0, len(records), self._chunk_size)):
            chunk = records[start : start + self._chunk_size]
            self._write_records(
                chunk,
                filename_pattern.format(chunk=chunk_number),
                columns,
            )

    def _write_records(
        self,
        records: Iterable[T],
        filename: str,
        columns: list[str],
    ) -> None:
        rows = [asdict(record) for record in records]
        df = pd.DataFrame(rows)
        if "sample_start" in df.columns:
            df = df.rename(columns={"sample_start": "a[k]"})
        if df.empty:
            df = pd.DataFrame(columns=columns)
        else:
            df = df.reindex(columns=columns)
        self._write_dataframe(df, filename)

    def _write_candidate_ranges(
        self,
        protease: str,
        ranges: list[tuple[str, int, int]],
    ) -> None:
        df = pd.DataFrame(ranges, columns=["uniprot_id", "start", "end"])
        self._write_dataframe(df, f"temp_negative_data_{protease}.csv")

    def _write_dataframe(self, df: pd.DataFrame, filename: str) -> None:
        df.to_csv(self._output_dir / filename, index=False)
