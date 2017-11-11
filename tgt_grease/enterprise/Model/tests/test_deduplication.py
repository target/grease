from unittest import TestCase
from tgt_grease.enterprise.Model import Deduplication
import datetime
import hashlib


class TestDeduplication(TestCase):

    def test_comparison(self):
        self.assertTrue(Deduplication.string_match_percentage("Hello", "Hallo") == 0.8)

    def test_generate_expiry_time(self):
        self.assertTrue(
            Deduplication.generate_expiry_time(12).hour == (datetime.datetime.utcnow() + datetime.timedelta(hours=12)).hour
        )

    def test_generate_max_expiry_time(self):
            print(str(Deduplication.generate_max_expiry_time(7)))
            print(str(datetime.datetime.utcnow() + datetime.timedelta(days=7)))
            self.assertTrue(
                Deduplication.generate_max_expiry_time(7).day == (datetime.datetime.utcnow() + datetime.timedelta(days=7)).day
            )

    def test_generate_hash(self):
        obj = {'test': 'var', 'test1': 5, 'test2': 7.89}
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )

    def test_generate_hash_multi_str_type(self):
        obj = {'test': u'var', 'test1': 5, 'test2': 7.89, 'test3': 'ver'}
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )

    def test_generate_hash_other_type(self):
        obj = 7
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )
        obj = 'test'
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )
        obj = u'test'
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )
        obj = 7.8
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )
        obj = ['test', 'var', 8, 8.43]
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj)).hexdigest()
        )
