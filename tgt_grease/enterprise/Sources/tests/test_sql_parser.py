from unittest import TestCase
from tgt_grease.enterprise.Sources import sql_source
from tgt_grease.core import Configuration
import json
import os
import datetime
import pyodbc


class TestSQLSource(TestCase):

    def test_type(self):
        inst = sql_source()
        self.assertTrue(isinstance(inst, sql_source))

    def __setup(self, conn):
        with conn.cursor() as cursor:
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

    def __teardown(self, conn):
        with conn.cursor() as cursor:
            cursor.execute("""
                DROP TABLE public.test_data
            """)
            conn.commit()


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
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            self.assertTrue(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                # TODO: Figure out how to determine what type
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

            self.__teardown(conn)


    def test_sql_parser_hour_good(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

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

            self.__teardown(conn)


    def test_sql_parser_minute_good(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

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

            self.__teardown(conn)


    def test_sql_parser_hour_and_minute_good(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

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

            self.__teardown(conn)


    def test_sql_parser_hour_bad(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            self.assertTrue(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                'type': 'postgresql',
                'dsn': 'GREASE_TEST_DSN',
                'query': 'select * from test_data;',
                'hour': (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).hour,
                'logic': {}
            }))
            data = source.get_data()

            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 0)

            self.__teardown(conn)

        self.__cleanup_schema()

    def test_sql_parser_minute_bad(self):
        self.__ensure_schema()
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            self.assertTrue(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                'type': 'postgresql',
                'dsn': 'GREASE_TEST_DSN',
                'query': 'select * from test_data;',
                'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).minute,
                'logic': {}
            }))
            data = source.get_data()

            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 0)

            self.__teardown(conn)


    def test_sql_parser_hour_and_minute_bad(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            self.assertTrue(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                'type': 'postgresql',
                'dsn': 'GREASE_TEST_DSN',
                'query': 'select * from test_data;',
                'hour': (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).hour,
                'minute': (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).minute,
                'logic': {}
            }))
            data = source.get_data()
            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 0)

            self.__teardown(conn)


    def test_sql_parser_insert(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            cursor = conn.cursor()
            result = cursor.execute("SELECT * FROM test_data").fetchall()

            self.assertTrue(len(result), 1)

            self.assertFalse(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                'type': 'postgresql',
                'dsn': 'GREASE_TEST_DSN',
                'query': """
                    INSERT INTO
                      test_data
                    (name_fs, name_ls)
                    VALUES 
                    ('sammy', 'sue');
                """,
                'logic': {}
            }))
            data = source.get_data()
            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 0)

            # Ensure nothing was actually inserted
            result = cursor.execute("SELECT * FROM test_data").fetchall()
            self.assertTrue(len(result), 1)
            cursor.close()

            self.__teardown(conn)


    def test_sql_parser_update(self):
        with pyodbc.connect(os.environ['GREASE_TEST_DSN']) as conn:
            source = sql_source()

            self.__setup(conn)

            cursor = conn.cursor()
            result = cursor.execute("SELECT * FROM test_data").fetchall()

            self.assertTrue(len(result), 1)
            self.assertEqual(result[0][0], 'sally')

            self.assertFalse(source.parse_source({
                'name': 'example_source',
                'job': 'example_job',
                'exe_env': 'general',
                'source': 'sql_source',
                'type': 'postgresql',
                'dsn': 'GREASE_TEST_DSN',
                'query': """
                    UPDATE Inventory
                    SET name_fs='sammy'
                    WHERE name_fs='sally';
                """,
                'logic': {}
            }))
            data = source.get_data()
            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 0)

            # Ensure nothing was actually updated
            result = cursor.execute("SELECT * FROM test_data").fetchall()
            self.assertTrue(len(result), 1)
            self.assertEqual(result[0][0], 'sally')

            cursor.close()

            self.__teardown(conn)

