from __future__ import annotations

from collections.abc import Iterable

import numpy as np


class SequenceWindowExtractor:
    """Pure sequence operations shared by positive and negative generation."""

    def __init__(self, trim_len: int, padding_char: str = "-") -> None:
        if trim_len <= 0 or trim_len % 2 != 0:
            raise ValueError("trim_len must be a positive even integer")
        if len(padding_char) != 1:
            raise ValueError("padding_char must be one character")
        self.trim_len = trim_len
        self.half = trim_len // 2
        self.padding_char = padding_char

    def positive_window(self, sequence: str, p1: int) -> str:
        start = p1 - self.half
        end = p1 + self.half

        left_pad = max(0, -start)
        right_pad = max(0, end - len(sequence))
        sequence_part = sequence[max(0, start) : min(len(sequence), end)]

        result = (
            self.padding_char * left_pad
            + sequence_part
            + self.padding_char * right_pad
        )
        if len(result) != self.trim_len:
            raise AssertionError(
                f"Expected positive window length {self.trim_len}, got {len(result)}"
            )
        return result

    def safe_ranges(
        self,
        sequence_length: int,
        cleavage_positions: Iterable[int],
    ) -> list[tuple[int, int]]:
        """Return inclusive index ranges outside every known positive window."""
        allowed = np.ones(sequence_length, dtype=bool)
        for p1 in cleavage_positions:
            start = max(0, int(p1) - self.half)
            end_exclusive = min(sequence_length, int(p1) + self.half)
            allowed[start:end_exclusive] = False

        indices = np.flatnonzero(allowed)
        return self._contiguous_ranges(indices)

    def ranges_outside_one_site(
        self,
        sequence_length: int,
        p1: int,
    ) -> list[tuple[int, int]]:
        return self.safe_ranges(sequence_length, [p1])

    def sample_windows_from_ranges(
        self,
        sequence: str,
        ranges: Iterable[tuple[int, int]],
        rng: np.random.RandomState,
    ) -> list[tuple[str, int, int, int]]:
        """Create approximately one random negative window per trim_len residues.

        Returns tuples of: (window, range_start, range_end, sample_start).
        Ranges use inclusive coordinates.
        """
        samples: list[tuple[str, int, int, int]] = []
        for range_start, range_end in ranges:
            available_length = range_end - range_start + 1
            repeat_num = available_length // self.trim_len
            if repeat_num <= 0:
                continue

            max_start = range_end - self.trim_len + 1
            candidates = np.arange(range_start, max_start + 1, dtype=int)
            rng.shuffle(candidates)

            for sample_start in candidates[:repeat_num]:
                start = int(sample_start)
                window = sequence[start : start + self.trim_len]
                if len(window) != self.trim_len:
                    continue
                samples.append((window, range_start, range_end, start))
        return samples

    @staticmethod
    def _contiguous_ranges(indices: np.ndarray) -> list[tuple[int, int]]:
        if len(indices) == 0:
            return []

        ranges: list[tuple[int, int]] = []
        start = int(indices[0])
        previous = int(indices[0])
        for raw_index in indices[1:]:
            index = int(raw_index)
            if index != previous + 1:
                ranges.append((start, previous))
                start = index
            previous = index
        ranges.append((start, previous))
        return ranges
