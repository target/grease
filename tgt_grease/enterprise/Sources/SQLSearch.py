from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core import Configuration
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
            'dsn': 'SQL_SERVER_CONNECTION', # <-- String representing the Environment variable used to connect with
            'query': 'select count(*) as order_total from orders where oDate::DATE = current_data', # <-- SQL Query to execute on server
            'query': {}, # <-- Dict of ElasticSearch Query
            'logic': {} # <-- Whatever logic your heart desires
        }

    """

    def parse_source(self, configuration):
        """This will Query the SQL Server to find data

        Args:
            configuration (dict): Configuration of Source. See Class Documentation above for more info

        Returns:
            bool: If True data will be scheduled for ingestion after deduplication. If False the engine will bail out

        """
        pass

    def mock_data(self, configuration):
        """Data from this source is mocked utilizing the GREASE Filesystem

        Mock data for this source can be place in `<GREASE_DIR>/etc/*.mock.sql.json`. This source will pick up all these
        files and load them into the returning object. The data in these files should reflect what you expect to return
        from SQL

        Args:
            configuration (dict): Configuration Data for source

        Note:
            Argument **configuration** is not honored here

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
