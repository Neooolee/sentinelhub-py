"""
Module that collects configuration data from config.json
"""

import os.path
import json
from collections import OrderedDict

# pylint: disable=E0203


class SHConfig:
    """ This is a singleton implementation of the sentinelhub configuration class.

    The class reads during its first initialisation the configurable settings from
    ``./config.json`` file:

        - `instance_id`: Users' instance id. User can set it to his/hers instance id in ``config.json`` instead
          of specifying it explicitly every time he/she creates new ogc request.
        - `ogc_base_url`: Base url for Sentinel Hub's services (should not be changed by the user).
        - `gpd_base_url`: Base url for Geopedia's services (should not be changed by the user).
        - `aws_base_url`: Base url for Sentinel-2 data on AWS (should not be changed by the user).
        - `aws_website_url`: Base url for AWS' public Sentinel-2 image browser.
        - `opensearch_url`: Base url for Sentinelhub Opensearch service.
        - `max_wfs_records_per_query`: Maximum number of records returned for each WFS query.
        - `max_opensearch_records_per_query`: Maximum number of records returned for each Opensearch query.
        - `default_start_date`: In case time parameter for OGC data requests is not specified this will be used for
          start date of the interval.
        - `max_download_attempts`: Maximum number of download attempts from a single URL until an error will be raised.
        - `download_sleep_time`: Number of seconds between the failed download attempt and the next attempt.
        - `download_timeout_seconds`: Maximum number of seconds before download attempt is canceled.

    Usage in the code:

        * ``SHConfig().ogc_base_url``
        * ``SHConfig().instance_id``

    """
    class _SHConfig:
        """
        Private class.
        """
        def __init__(self):
            self.config_params = ['instance_id', 'ogc_base_url', 'gpd_base_url', 'aws_base_url',
                                  'aws_website_url', 'opensearch_url', 'max_wfs_records_per_query',
                                  'max_opensearch_records_per_query', 'default_start_date',
                                  'max_download_attempts', 'download_sleep_time', 'download_timeout_seconds']
            self.load_configuration()

        def _check_configuration(self, config):
            """
            Checks if configuration file has contains all keys.

            :param config: configuration dictionary read from ``config.json``
            :type config: dict
            """

            for key in self.config_params:
                if key not in config:
                    raise ValueError('Configuration file does not contain %s key.' % key)
            if config['max_wfs_records_per_query'] > 100:
                raise ValueError("Value of config parameter 'max_wfs_records_per_query' must be at most 100")
            if config['max_opensearch_records_per_query'] > 500:
                raise ValueError("Value of config parameter 'max_opensearch_records_per_query' must be at most 500")

        @staticmethod
        def _get_config_file():
            """Checks if configuration file exists and returns its file path

            :return: location of configuration file
            :rtype: str
            """
            package_dir = os.path.dirname(__file__)
            config_file = os.path.join(package_dir, 'config.json')

            if not os.path.isfile(config_file):
                raise IOError('Configuration file does not exist: %s' % os.path.abspath(config_file))

            return config_file

        def load_configuration(self):
            """
            Method reads and loads the configuration file.
            """
            with open(self._get_config_file(), 'r') as cfg_file:
                config = json.load(cfg_file)
                self._check_configuration(config)

                for prop in config:
                    if prop in self.config_params:
                        setattr(self, prop, config[prop])

                if not self.instance_id:
                    self.instance_id = None

        def save_configuration(self):
            """
            Method saves changed parameter values to the configuration file.
            """
            config = OrderedDict((prop, getattr(self, prop)) for prop in self.config_params)
            self._check_configuration(config)

            with open(self._get_config_file(), 'w') as cfg_file:
                json.dump(config, cfg_file, indent=2)

    _instance = None

    def __init__(self):
        if not SHConfig._instance:
            SHConfig._instance = self._SHConfig()

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __dir__(self):
        return sorted(super(SHConfig, self).__dir__() + self._instance.config_params)

    def save(self):
        """Method that saves configuration parameter changes from instance of SHConfig class to global config class and
        to ``config.json`` file.

        Example of use case
            ``my_config = SHConfig()`` \n
            ``my_config.instance_id = '<new instance id>'`` \n
            ``my_config.save()``
        """
        for prop in self._instance.config_params:
            setattr(self._instance, prop, getattr(self, prop))
        self._instance.save_configuration()
