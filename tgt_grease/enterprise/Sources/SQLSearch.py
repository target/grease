from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core import Configuration, GreaseContainer
import pyodbc
import datetime
import fnmatch
import json
import os
import sys


class SQLSource(BaseSourceClass):
    """Source data from a SQL Database

    This Source is designed to query a SQL Server for data. A generic configuration looks like this for a
    sql_source::

        {
            'name': 'example_source', # <-- A name
            'job': 'example_job', # <-- Any job you want to run
            'exe_env': 'general', # <-- Selected execution environment; Can be anything!
            'source': 'sql_source', # <-- This source
            'type': 'postgresql', # <-- SQL Server Type (Only supports PostgreSQL Currently)
            'dsn': 'SQL_SERVER_CONNECTION', # <-- String representing the Environment variable used to connect with
            'query': 'select count(*) as order_total from orders where oDate::DATE = current_data', # <-- SQL Query to execute on server
            'hour': 16, # <-- **OPTIONAL** 24hr time hour to poll SQL
            'minute': 30, # <-- **OPTIONAL** Minute to poll SQL
            'logic': {} # <-- Whatever logic your heart desires
        }

    Note:
        This configuration is an example
    Note:
        Currently We only support PostreSQL Server
    Note:
        without `minute` parameter the engine will poll for the entire hour
    Note:
        **Hour and minute parameters are in UTC time**
    Note:
        To only poll once an hour only set the **minute** field

    """

    def parse_source(self, configuration):
        """This will Query the SQL Server to find data

        Args:
            configuration (dict): Configuration of Source. See Class Documentation above for more info

        Returns:
            bool: If True data will be scheduled for ingestion after deduplication. If False the engine will bail out

        """
        if configuration.get('hour'):
            if datetime.datetime.utcnow().hour != int(configuration.get('hour')):
                # it is not the correct hour
                return True
        if configuration.get('minute'):
            if datetime.datetime.utcnow().minute != int(configuration.get('minute')):
                # it is not the correct hour
                return True
        else:
            # Attempt to get the DSN for the connection
            ioc = GreaseContainer()
            if os.environ.get(configuration.get('dsn')) and configuration.get('query'):
                # ensure the DSN is setup and the query is present
                try:
                    DSN = os.environ.get(configuration.get('dsn'))

                    connection_string= "{0}".format(DSN)

                    conn = pyodbc.connect(connection_string)

                    # See the following:
                    # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-PostgreSQL
                    # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-MySQL
                    if configuration.get('type').lower() in ['postgresql', 'mysql']:
                        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                        conn.setencoding(encoding='utf-8')

                        if sys.version_info[:2] == (2, 7):
                            conn.setencoding(unicode, encoding='utf-8', ctype=pyodbc.SQL_CHAR)

                except Exception as e:
                    # Naked except to prevent issues around connections
                    ioc.getLogger().error("Error connecting to database; Error [{0}]".format(e), notify=False)
                    del ioc
                    return False

                try:
                    # Open a cursor and execute a query, then grab the rows as our data
                    with conn.cursor() as cursor:
                        cursor.execute(configuration.get('query'))
                        # Convert the results from tuples with just values to dicts with column names
                        # e.g (1, 'Sally', 'Sue') -> {'id': 1, 'name_first': 'Sally', 'name_last': 'Sue'}
                        # Adapted from https://stackoverflow.com/questions/16519385/output-pyodbc-cursor-results-as-python-dictionary
                        self._data = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

                except pyodbc.ProgrammingError as e:
                    # It's likely a non-SELECT query was attempted, then fetchall() was called on the results
                    # which will throw this exception
                    ioc.getLogger().error(
                        "Error executing query [{0}]; Error [{1}] - NOTE: Only SELECT queries are allowed"
                        .format(configuration.get('query'), e),
                        notify=False
                    )
                    return False

                finally:
                    del ioc
                    conn.rollback()
                    conn.close()

                return True

            else:
                # could not get the DSN
                ioc.getLogger().error("Failed to locate the DSN environment variable", notify=False)
                del ioc
                return False

    def mock_data(self, configuration):
        """Data from this source is mocked utilizing the GREASE Filesystem

        Mock data for this source can be place in `<GREASE_DIR>/etc/*.mock.sql.json`. This source will pick up all these
        files and load them into the returning object. The data in these files should reflect what you expect to return
        from SQL::

            {
                'column expected': 'value expected'
                ...
            }

        Args:
            configuration (dict): Configuration Data for source

        Note:
            Argument **configuration** is not honored here
        Note:
            A mock file should represent a single row

        Returns:
            list[dict]: Mocked Data

        """
        intermediate = list()
        matches = []
        conf = Configuration()
        for root, dirnames, filenames in os.walk(conf.greaseDir + 'etc'):
            for filename in fnmatch.filter(filenames, '*.mock.sql.json'):
                matches.append(os.path.join(root, filename))
        for doc in matches:
            with open(doc) as current_file:
                content = current_file.read().replace('\r', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        return intermediate
