from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core import Configuration, GreaseContainer
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import fnmatch
import json
import os


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
        ioc = GreaseContainer()
        if configuration.get('hour'):
            if datetime.datetime.utcnow().hour != int(configuration.get('hour')):
                # it is not the correct hour
                return True
        if configuration.get('minute'):
            if datetime.datetime.utcnow().minute != int(configuration.get('minute')):
                # it is not the correct hour
                return True
        if configuration.get('type') != 'postgresql':
            ioc.getLogger().error("Unsupported SQL Server Type; Currently Only supporting PostgreSQL", notify=False)
            return False
        else:
            # Attempt to get the DSN for the connection
            if os.environ.get(configuration.get('dsn')) and configuration.get('query'):
                # ensure the DSN is setup and the query is present
                try:
                    DSN = os.environ.get(configuration.get('dsn'))
                    with psycopg2.connect(DSN) as conn:
                        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                            cursor.execute(configuration.get('query'))
                            data = cursor.fetchall()
                            for row in data:
                                self._data.append(row)
                            del ioc
                    return True
                except Exception as e:
                    # Naked except to prevent issues around connections
                    ioc.getLogger().error("Error processing configuration; Error [{0}]".format(e.message), notify=False)
                    del ioc
                    return False
            else:
                # could not get the DSN
                ioc.getLogger().error("Failed to locate the DSN variable", notify=False)
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
                content = current_file.read().replace('\r\n', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        return intermediate
