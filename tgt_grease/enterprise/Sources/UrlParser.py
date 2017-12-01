from tgt_grease.enterprise.Model import BaseSourceClass
from tgt_grease.core import Configuration
import json
import fnmatch
import os
import requests
import datetime


class URLParser(BaseSourceClass):
    """Monitor URL's as a source of information

    This source is designed to provide source data on the URL's configured for a GREASE sourcing cluster. A generic
    configuration looks like this for a url_source::

        {
            'name': 'example_source', # <-- A name
            'job': 'example_job', # <-- Any job you want to run
            'exe_env': 'general', # <-- Selected execution environment; Can be anything!
            'source': 'url_source', # <-- This source
            'url': ['google.com', 'http://bing.com', '8.8.8.8'], # <-- List of URL's to parse
            'hour': 16, # <-- **OPTIONAL** 24hr time hour to poll URLs
            'minute': 30, # <-- **OPTIONAL** Minute to poll URLs
            'logic': {} # <-- Whatever logic your heart desires
        }

    Note:
        This configuration is an example
    Note:
        If a URL in the `url` parameter is not prefixed with `http://` then the class will do so for you
    Note:
        without `minute` parameter the engine will poll for the entire hour
    Note:
        **Hour and minute parameters are in UTC time**
    Note:
        To only poll once an hour only set the **minute** field

    """

    def parse_source(self, configuration):
        """This will make a GET request to all URL's in the list provided by your configuration

        Args:
            configuration (dict): Configuration of Source. See Class Documentation above for more info

        Returns:
            bool: If True data will be scheduled for ingestion after deduplication. If False the engine will bail out

        """
        scannable = len(configuration.get('url', []))
        if scannable is 0:
            return False
        scanned = 0
        if configuration.get('hour'):
            if datetime.datetime.utcnow().hour != int(configuration.get('hour')):
                # it is not the correct hour
                return True
        if configuration.get('minute'):
            if datetime.datetime.utcnow().minute != int(configuration.get('minute')):
                # it is not the correct hour
                return True
        for URL in configuration.get('url', []):  # type: str
            if not URL.startswith("http://"):
                URL = "http://" + URL
            try:
                response = requests.get(URL)
                self._data.append({
                    'url': response.url.encode('utf-8', 'ignore'),
                    'status_code': int(response.status_code),
                    'headers': str(response.headers),
                    'body': response.text.encode('utf-8', 'ignore')
                })
                scanned += 1
            except requests.HTTPError:
                continue
        if scanned < (scannable / 2):
            return False
        else:
            return True

    def mock_data(self, configuration):
        """Data from this source is mocked utilizing the GREASE Filesystem

        Mock data for this source can be place in `<GREASE_DIR>/etc/*.mock.url.json`. This source will pick up all these
        files and load them into the returning object. They will need to follow this schema::

            {
                'url': String, # <-- URL that would have been loaded
                'status_code': Int, # <-- HTTP Status code
                'headers': String, # <-- HTTP headers as a string
                'body': String # <-- HTTP response body
            }

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
            for filename in fnmatch.filter(filenames, '*.mock.url.json'):
                matches.append(os.path.join(root, filename))
        for doc in matches:
            with open(doc) as current_file:
                content = current_file.read().replace('\r\n', '')
            try:
                intermediate.append(json.loads(content))
            except ValueError:
                continue
        return intermediate
