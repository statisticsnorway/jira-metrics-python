from jiracollector import JiraCollector
import requests
from unittest import mock
import unittest
import pytest
import json
import google.auth
import google.cloud 
from google.cloud import secretmanager
#from google.cloud.secretmanager import SecretManagerServiceClient

import logging.config
import configparser


config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)
logger = logging.getLogger()

@mock.patch('google.auth.default', side_effect=mock.Mock(side_effect=Exception('Test')),autospec=True)
def test_that_getApiKey_raises_exception(mock_google_api):
    with pytest.raises(Exception):
        assert JiraCollector("not needed") 
    
#@mock.patch('google.auth.default')
#@mock.patch('secretmanager.SecretManagerServiceClient')
#@mock.patch('secretmanager.SecretManagerServiceClient.secret_version_path')
#@mock.patch('secretmanager.SecretManagerServiceClient.access_secret_version')
#def test_secret_manager_secret_exception(mock_auth, mock_client, #mock_secret_version_path, mock_secret_version_data):
#    mock_auth.return_value = ""
#    mock_client.return_value = ""
#    mock_secret_version_path.return_value = ""
#    mock_secret_version_data.return_value = ""
#    assert JiraCollector("not needed") 
 