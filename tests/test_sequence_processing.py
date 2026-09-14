import unittest

import numpy as np

from protease_dataset.services.sequence_processing import SequenceWindowExtractor
from protease_dataset.services.uniprot_id import InvalidUniProtIdError, UniProtIdNormalizer


class UniProtIdNormalizerTest(unittest.TestCase):
    def test_exact_six_chars(self):
        self.assertEqual(UniProtIdNormalizer().normalize("P51170"), "P51170")

    def test_legacy_suffix_is_trimmed(self):
        self.assertEqual(UniProtIdNormalizer().normalize("P51170_extra"), "P51170")

    def test_invalid_id_raises(self):
        with self.assertRaises(InvalidUniProtIdError):
            UniProtIdNormalizer().normalize("ABC")


class SequenceWindowExtractorTest(unittest.TestCase):
    def test_positive_window_middle(self):
        extractor = SequenceWindowExtractor(4)
        self.assertEqual(extractor.positive_window("ABCDEFGH", 4), "CDEF")

    def test_positive_window_left_padding(self):
        extractor = SequenceWindowExtractor(4)
        self.assertEqual(extractor.positive_window("ABCDEFGH", 1), "-ABC")

    def test_positive_window_right_padding(self):
        extractor = SequenceWindowExtractor(4)
        self.assertEqual(extractor.positive_window("ABCDEFGH", 7), "FGH-")

    def test_safe_ranges_exclude_all_known_sites(self):
        extractor = SequenceWindowExtractor(4)
        self.assertEqual(extractor.safe_ranges(12, [4, 9]), [(0, 1), (6, 6), (11, 11)])

    def test_negative_samples_never_overlap_excluded_window(self):
        extractor = SequenceWindowExtractor(4)
        sequence = "ABCDEFGHIJKLMNOP"
        ranges = extractor.safe_ranges(len(sequence), [8])
        samples = extractor.sample_windows_from_ranges(
            sequence,
            ranges,
            np.random.RandomState(42),
        )
        for _, _, _, sample_start in samples:
            sample_indices = set(range(sample_start, sample_start + 4))
            excluded = set(range(6, 10))
            self.assertTrue(sample_indices.isdisjoint(excluded))


if __name__ == "__main__":
    unittest.main()
