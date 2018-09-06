from unittest import TestCase
from tgt_grease.core import Configuration
from tgt_grease.enterprise.Sources import url_source
import json
import os
import datetime


class TestUrlParser(TestCase):

    def test_url_parser_empty(self):
        source = url_source()
        self.assertFalse(source.parse_source({}))
        self.assertFalse(source.get_data())

    def test_url_parser_mock(self):
        source = url_source()
        conf = Configuration()
        mock = {
            'url': 'https://google.com',
            'status_code': 200,
            'headers': str({'test': 'ver', 'test1': 'val'}),
            'body': 'welcome to google'
        }
        fil = open(conf.greaseDir + 'etc' + conf.fs_sep + 'test.mock.url.json', 'w')
        fil.write(json.dumps(mock))
        fil.close()
        mockData = source.mock_data({})
        self.assertEqual(len(mockData), 1)
        self.assertEqual(mock.get('url'), mockData[0].get('url'))
        self.assertEqual(mock.get('status_code'), mockData[0].get('status_code'))
        self.assertEqual(mock.get('headers'), mockData[0].get('headers'))
        self.assertEqual(mock.get('body'), mockData[0].get('body'))
        os.remove(conf.greaseDir + 'etc' + conf.fs_sep + 'test.mock.url.json')

    def test_url_parser_single_source(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 1)
        self.assertEqual(b'http://www.google.com/', Data[0].get('url'))
        self.assertEqual(200, Data[0].get('status_code'))

    def test_url_parser_multiple_source(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'url': ['google.com', 'bing.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 2)

    def test_url_parser_test_hour_good(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'hour': datetime.datetime.utcnow().hour,
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 1)
        self.assertEqual(b'http://www.google.com/', Data[0].get('url'))
        self.assertEqual(200, Data[0].get('status_code'))

    def test_url_parser_test_minute_good(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'minute': datetime.datetime.utcnow().minute,
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 1)
        self.assertEqual(b'http://www.google.com/', Data[0].get('url'))
        self.assertEqual(200, Data[0].get('status_code'))

    def test_url_parser_test_hour_and_minute_good(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'hour': datetime.datetime.utcnow().hour,
            'minute': datetime.datetime.utcnow().minute,
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 1)
        self.assertEqual(b'http://www.google.com/', Data[0].get('url'))
        self.assertEqual(200, Data[0].get('status_code'))

    def test_url_parser_test_minute_bad(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).minute + 7,
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 0)

    def test_url_parser_test_hour_and_minute_bad(self):
        source = url_source()
        self.assertTrue(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'url_source',
            'hour': (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).hour,
            'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).minute + 7,
            'url': ['google.com'],
            'logic': {}
        }))
        Data = source.get_data()
        self.assertEqual(len(Data), 0)
