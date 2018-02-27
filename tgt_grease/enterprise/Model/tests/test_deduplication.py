from unittest import TestCase
from tgt_grease.enterprise.Model import Deduplication
from tgt_grease.core import GreaseContainer
import datetime
import hashlib
import uuid
import time


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
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )

    def test_generate_hash_multi_str_type(self):
        obj = {'test': u'var', 'test1': 5, 'test2': 7.89, 'test3': 'ver'}
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )

    def test_generate_hash_other_type(self):
        obj = 7
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )
        obj = 'test'
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )
        obj = u'test'
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )
        obj = 7.8
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )
        obj = ['test', 'var', 8, 8.43]
        self.assertEqual(
            Deduplication.generate_hash_from_obj(obj),
            hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        )

    def test_object_score_low_duplication(self):
        obj1 = {
            'field1': 'value',
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        obj2 = {
            'field1': str(uuid.uuid4()),
            'field2':  str(uuid.uuid4()),
            'field3':  str(uuid.uuid4()),
            'field4':  str(uuid.uuid4()),
            'field5':  str(uuid.uuid4())
        }
        ioc = GreaseContainer()
        parent1 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj1)
        }).inserted_id
        score1 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj1,
            parent1,
            1,
            1
        )
        parent2 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj2)
        }).inserted_id
        score2 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj2,
            parent2,
            1,
            1
        )
        print("++++++++++++++++++++++++++++++++++")
        print("score1: {0}".format(score1))
        print("score2: {0}".format(score2))
        print("++++++++++++++++++++++++++++++++++")
        self.assertTrue(score1 == 0.0)
        self.assertTrue(score2 <= 20.0)
        ioc.getCollection('test_scoring').drop()
        time.sleep(1.5)

    def test_object_score_medium_duplication(self):
        obj1 = {
            'field1': 'value',
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        obj2 = {
            'field1': str(uuid.uuid4()),
            'field2': 'value1',
            'field3': 'value2',
            'field4':  str(uuid.uuid4()),
            'field5':  str(uuid.uuid4())
        }
        ioc = GreaseContainer()
        parent1 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj1)
        }).inserted_id
        score1 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj1,
            parent1,
            1,
            1
        )
        parent2 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj2)
        }).inserted_id
        score2 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj2,
            parent2,
            1,
            1
        )
        print("++++++++++++++++++++++++++++++++++")
        print("score1: {0}".format(score1))
        print("score2: {0}".format(score2))
        print("++++++++++++++++++++++++++++++++++")
        self.assertTrue(score1 == 0.0)
        self.assertTrue(score2 <= 50.0)
        ioc.getCollection('test_scoring').drop()
        time.sleep(1.5)

    def test_object_score_high_duplication(self):
        obj1 = {
            'field1': 'value',
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        obj2 = {
            'field1': str(uuid.uuid4()),
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        ioc = GreaseContainer()
        parent1 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj1)
        }).inserted_id
        score1 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj1,
            parent1,
            1,
            1
        )
        parent2 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj2)
        }).inserted_id
        score2 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj2,
            parent2,
            1,
            1
        )
        print("++++++++++++++++++++++++++++++++++")
        print("score1: {0}".format(score1))
        print("score2: {0}".format(score2))
        print("++++++++++++++++++++++++++++++++++")
        self.assertTrue(score1 == 0.0)
        self.assertTrue(score2 >= 80.0)
        ioc.getCollection('test_scoring').drop()
        time.sleep(1.5)

    def test_object_score_maximum_duplication(self):
        obj1 = {
            'field1': 'value',
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        obj2 = {
            'field1': 'value',
            'field2': 'value1',
            'field3': 'value2',
            'field4': 'value3',
            'field5': 'value4'
        }
        ioc = GreaseContainer()
        parent1 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj1)
        }).inserted_id
        score1 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj1,
            parent1,
            1,
            1
        )
        parent2 = ioc.getCollection('test_scoring').insert_one({
            'expiry': Deduplication.generate_expiry_time(1),
            'max_expiry': Deduplication.generate_max_expiry_time(1),
            'type': 1,
            'score': 1,
            'source': 'test_source',
            'hash': Deduplication.generate_hash_from_obj(obj2)
        }).inserted_id
        score2 = Deduplication.object_field_score(
            'test_scoring',
            ioc,
            'test_source',
            'test_configuration',
            obj2,
            parent2,
            1,
            1
        )
        print("++++++++++++++++++++++++++++++++++")
        print("score1: {0}".format(score1))
        print("score2: {0}".format(score2))
        print("++++++++++++++++++++++++++++++++++")
        self.assertTrue(score1 == 0.0)
        self.assertTrue(score2 == 100.0)
        ioc.getCollection('test_scoring').drop()
        time.sleep(1.5)

    def test_deduplicate_object(self):
        ioc = GreaseContainer()
        ioc.getConfig().set('verbose', True, 'Logging')
        obj = [
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': 'var1',
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': 'var4',
                'field5': str(uuid.uuid4()),
            }
        ]
        finalObj = []
        Deduplication.deduplicate_object(
            ioc,
            obj[0],
            1,
            1,
            40.0,
            'test_source',
            'test_configuration',
            finalObj,
            'test_source'
        )
        self.assertEqual(len(finalObj), 1)
        Deduplication.deduplicate_object(
            ioc,
            obj[1],
            1,
            1,
            40.0,
            'test_source',
            'test_configuration',
            finalObj,
            'test_source'
        )
        self.assertEqual(len(finalObj), 1)
        Deduplication.deduplicate_object(
            ioc,
            obj[2],
            1,
            1,
            40.0,
            'test_source',
            'test_configuration',
            finalObj,
            'test_source'
        )
        self.assertGreaterEqual(len(finalObj), 1)
        ioc.getConfig().set('verbose', False, 'Logging')
        ioc.getCollection('test_source').drop()
        time.sleep(1.5)

    def test_deduplication(self):
        ioc = GreaseContainer()
        dedup = Deduplication(ioc)
        ioc.getConfig().set('verbose', True, 'Logging')
        obj = [
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': 'var',
                'field1': 'var1',
                'field2': 'var2',
                'field3': 'var3',
                'field4': 'var4',
                'field5': 'var5',
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            },
            {
                'field': str(uuid.uuid4()),
                'field1': str(uuid.uuid4()),
                'field2': str(uuid.uuid4()),
                'field3': str(uuid.uuid4()),
                'field4': str(uuid.uuid4()),
                'field5': str(uuid.uuid4())
            }
        ]
        finalObj = dedup.Deduplicate(
            obj,
            'test_source',
            'test_configuration',
            85.0,
            1,
            1,
            'test_source'
        )
        self.assertGreaterEqual(len(finalObj), 4)
        ioc.getConfig().set('verbose', False, 'Logging')
        ioc.getCollection('test_source').drop()
        time.sleep(1.5)
