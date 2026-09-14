import unittest

from protease_dataset.domain import CleavageSite
from protease_dataset.infrastructure.cached_sequence_provider import CachingProteinSequenceProvider
from protease_dataset.services.negative_dataset import NegativeDatasetService
from protease_dataset.services.positive_dataset import PositiveDatasetService
from protease_dataset.services.sequence_processing import SequenceWindowExtractor
from protease_dataset.services.uniprot_id import UniProtIdNormalizer


class FakeProvider:
    def __init__(self, sequences):
        self.sequences = sequences
        self.calls = 0

    def get_sequence(self, uniprot_id):
        self.calls += 1
        return self.sequences[uniprot_id]


class DatasetServiceTest(unittest.TestCase):
    def setUp(self):
        self.raw_provider = FakeProvider({"P51170": "A" * 40})
        self.provider = CachingProteinSequenceProvider(self.raw_provider)
        self.normalizer = UniProtIdNormalizer()
        self.extractor = SequenceWindowExtractor(8)

    def test_positive_and_negative_share_cached_sequence(self):
        sites = [CleavageSite("P51170", 12), CleavageSite("P51170", 24)]
        positive = PositiveDatasetService(
            self.provider,
            self.normalizer,
            self.extractor,
        )
        negative = NegativeDatasetService(
            self.provider,
            self.normalizer,
            self.extractor,
            random_seed=42,
        )

        pos_result = positive.generate("S01.247", 567, sites)
        neg_result = negative.generate("S01.247", 567, sites)

        self.assertEqual(len(pos_result.records), 2)
        self.assertGreaterEqual(len(neg_result.records), 1)
        self.assertEqual(self.raw_provider.calls, 1)

    def test_negative_windows_exclude_both_cleavage_sites(self):
        sequence = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcd"
        raw_provider = FakeProvider({"P51170": sequence})
        service = NegativeDatasetService(
            raw_provider,
            self.normalizer,
            SequenceWindowExtractor(8),
            random_seed=7,
        )
        sites = [CleavageSite("P51170", 12), CleavageSite("P51170", 24)]
        result = service.generate("S01.247", 567, sites)

        excluded = set(range(8, 16)) | set(range(20, 28))
        for record in result.records:
            sampled = set(range(record.sample_start, record.sample_start + 8))
            self.assertTrue(sampled.isdisjoint(excluded))


if __name__ == "__main__":
    unittest.main()
