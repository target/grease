from unittest import TestCase
from tgt_grease.enterprise.Detectors import Range


class TestRange(TestCase):

    def test_range_compare_min_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(5, {'min': 4}))
        self.assertTrue(r.range_compare(4.1, {'min': 4.0}))

    def test_range_compare_min_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(3, {'min': 4}))
        self.assertFalse(r.range_compare(3.9, {'min': 4.0}))

    def test_range_compare_max_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(3, {'max': 4}))
        self.assertTrue(r.range_compare(3.9, {'max': 4.0}))

    def test_range_compare_max_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {'max': 4}))
        self.assertFalse(r.range_compare(4.1, {'max': 4.0}))

    def test_range_compare_min_and_max_pass(self):
        r = Range()
        self.assertTrue(r.range_compare(3, {'max': 4, 'min': 1}))
        self.assertTrue(r.range_compare(3.9, {'max': 4.0, 'min': 1}))

    def test_range_compare_min_and_max_fail(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {'max': 4, 'min': 1}))
        self.assertFalse(r.range_compare(4.1, {'max': 4.0, 'min': 1}))

    def test_range_compare_no_min_or_max(self):
        r = Range()
        self.assertFalse(r.range_compare(5, {}))

    def test_range_compare_bad_field_type(self):
        r = Range()
        self.assertFalse(r.range_compare('cats', {'max': 4, 'min': 1}))

    def test_range_compare_bad_min_or_max(self):
        r = Range()
        self.assertFalse(r.range_compare(3, {'min': 'cat'}))
        self.assertFalse(r.range_compare(3.9, {'min': 'dog'}))
        self.assertFalse(r.range_compare(5, {'max': 'cat'}))
        self.assertFalse(r.range_compare(4.1, {'max': 'dog'}))
        self.assertFalse(r.range_compare(5, {'max': 'cat', 'min': 'bagel'}))
        self.assertFalse(r.range_compare(4.1, {'max': 'dog', 'min': 'bagel'}))
