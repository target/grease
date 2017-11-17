from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core import Configuration
import elasticsearch
import os
import fnmatch
import datetime
import json


class ElasticSource(BaseSourceClass):
    """Source data from ElasticSearch

    This Source is designed to query ElasticSearch for data. A generic configuration looks like this for a
    elastic_source::

        {
            'name': 'example_source', # <-- A name
            'job': 'example_job', # <-- Any job you want to run
            'exe_env': 'general', # <-- Selected execution environment; Can be anything!
            'source': 'elastic_source', # <-- This source
            'server': 'http://localhost:9200', # <-- String for ES Connection to occur
            'index': 'my_fake_index', # <-- Index to query within ES
            'doc_type': 'myData' # <-- Document type to query for in ES
            'query': {}, # <-- Dict of ElasticSearch Query
            'hour': 16, # <-- **OPTIONAL** 24hr time hour to poll SQL
            'minute': 30, # <-- **OPTIONAL** Minute to poll SQL
            'logic': {} # <-- Whatever logic your heart desires
        }

    Note:
        without `minute` parameter the engine will poll for the entire hour
    Note:
        **Hour and minute parameters are in UTC time**
    Note:
        To only poll once an hour only set the **minute** field

    """

    def parse_source(self, configuration):
        """This will make a ElasticSearch connection & query to the configured server

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
        if configuration.get('server') \
                and configuration.get('query') \
                and configuration.get('index') \
                and configuration.get('doc_type'):
            try:
                es = elasticsearch.Elasticsearch(
                    "".join(configuration.get('server')),
                    timeout=30,
                    max_retries=2,
                    retry_on_timeout=True
                )
            except BaseException:
                # Failed to connect to ES
                return False
            try:
                self._data = es.search(
                    index=''.join(configuration.get('index')),
                    doc_type=''.join(configuration.get('doc_type')),
                    body=configuration.get('query')
                )
            except elasticsearch.ImproperlyConfigured:
                # Improperly configured request
                return False
            except elasticsearch.ElasticsearchException:
                # generic exception
                return False
            del es
        else:
            # Invalid parameters
            return False

    def mock_data(self, configuration):
        """Data from this source is mocked utilizing the GREASE Filesystem

        Mock data for this source can be place in `<GREASE_DIR>/etc/*.mock.es.json`. This source will pick up all these
        files and load them into the returning object. The data in these files should reflect what you expect to return
        from ElasticSearch

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
            for filename in fnmatch.filter(filenames, '*.mock.es.json'):
                matches.append(os.path.join(root, filename))
        for doc in matches:
            with open(doc) as current_file:
                content = current_file.read().replace('\r\n', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        return intermediate
