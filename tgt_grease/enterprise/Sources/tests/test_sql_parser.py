from unittest import TestCase
from tgt_grease.enterprise.Sources import sql_source
from tgt_grease.core import Configuration
import json
import os
import psycopg2
import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class TestSQLSource(TestCase):

    def test_type(self):
        inst = sql_source()
        self.assertTrue(isinstance(inst, sql_source))

    def test_sql_parser_mock(self):
        source = sql_source()
        conf = Configuration()
        mock = {
            'id': 1,
            'name_fs': 'sally',
            'name_ls': 'sue'

        }
        fil = open(conf.greaseDir + 'etc' + conf.fs_sep + 'test.mock.sql.json', 'w')
        fil.write(json.dumps(mock))
        fil.close()
        mockData = source.mock_data({})
        self.assertEqual(len(mockData), 1)
        self.assertEqual(mock.get('id'), 1)
        self.assertEqual(mock.get('name_fs'), mockData[0].get('name_fs'))
        self.assertEqual(mock.get('name_ls'), mockData[0].get('name_ls'))
        os.remove(conf.greaseDir + 'etc' + conf.fs_sep + 'test.mock.sql.json')

    def test_sql_parser(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 1)
                self.assertIsInstance(data[0], dict)
                self.assertEqual(data[0].get('id'), 1)
                self.assertEqual(data[0].get('name_fs'), 'sally')
                self.assertEqual(data[0].get('name_ls'), 'sue')
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_bad_type(self):
        source = sql_source()
        self.assertFalse(source.parse_source({
            'name': 'example_source',
            'job': 'example_job',
            'exe_env': 'general',
            'source': 'sql_source',
            'type': 'mssql',
            'dsn': 'GREASE_TEST_DSN',
            'query': 'select * from test_data;',
            'logic': {}
        }))
        data = source.get_data()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 0)

    def test_sql_parser_hour_good(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'hour': datetime.datetime.utcnow().hour,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 1)
                self.assertIsInstance(data[0], dict)
                self.assertEqual(data[0].get('id'), 1)
                self.assertEqual(data[0].get('name_fs'), 'sally')
                self.assertEqual(data[0].get('name_ls'), 'sue')
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_minute_good(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'minute': datetime.datetime.utcnow().minute,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 1)
                self.assertIsInstance(data[0], dict)
                self.assertEqual(data[0].get('id'), 1)
                self.assertEqual(data[0].get('name_fs'), 'sally')
                self.assertEqual(data[0].get('name_ls'), 'sue')
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_hour_and_minute_good(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'hour': datetime.datetime.utcnow().hour,
                    'minute': datetime.datetime.utcnow().minute,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 1)
                self.assertIsInstance(data[0], dict)
                self.assertEqual(data[0].get('id'), 1)
                self.assertEqual(data[0].get('name_fs'), 'sally')
                self.assertEqual(data[0].get('name_ls'), 'sue')
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_hour_bad(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'hour': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).hour,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 0)
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_minute_bad(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).minute,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 0)
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)

    def test_sql_parser_hour_and_minute_bad(self):
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE DATABASE test_data;
                """)
        os.environ['GREASE_TEST_DSN'] = "host=localhost user=postgres dbname=test_data"
        with psycopg2.connect(os.environ['GREASE_TEST_DSN']) as conn:
            with conn.cursor() as cursor:
                source = sql_source()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS 
                      test_data
                    (
                        id SERIAL PRIMARY KEY NOT NULL,
                        name_fs VARCHAR,
                        name_ls VARCHAR
                    );
                """)
                conn.commit()
                cursor.execute("""
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sally', 'sue');
                """)
                conn.commit()
                self.assertTrue(source.parse_source({
                    'name': 'example_source',
                    'job': 'example_job',
                    'exe_env': 'general',
                    'source': 'sql_source',
                    'type': 'postgresql',
                    'dsn': 'GREASE_TEST_DSN',
                    'query': 'select * from test_data;',
                    'hour': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).hour,
                    'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).minute,
                    'logic': {}
                }))
                data = source.get_data()
                self.assertTrue(isinstance(data, list))
                self.assertEqual(len(data), 0)
                cursor.execute("""
                    DROP TABLE public.test_data
                """)
        with psycopg2.connect("host=localhost user=postgres") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute("""
                    DROP DATABASE test_data;
                """)
