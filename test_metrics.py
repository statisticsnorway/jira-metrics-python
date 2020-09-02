import logging.config
import configparser
import metrics
from datetime import datetime
import urllib.request
from unittest import mock
from requests import request
from aiohttp.web import Response


config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)

logger = logging.getLogger()

# Test the convertion from "json-metric" to string-metric 
def test_stringify_json_metrics():
    jsonMetrics = '{\'jira_total_done{project_name="BIP"}\': \'42\'}'
    assert metrics.stringifyJsonMetric(jsonMetrics) == "jira_total_done{project_name=\"BIP\"} 42\n"

# Test that internal metrics gets appended
def test_append_internal_metrics():
    strStartTime = '01/01/20 12:00:00'
    start = datetime.strptime(strStartTime, '%m/%d/%y %H:%M:%S')
    strEndTime = '01/01/20 12:00:42'
    end = datetime.strptime(strEndTime, '%m/%d/%y %H:%M:%S')

    jsonMetrics = '{\'jira_total_done{project_name="BIP"}\': \'42\'}'
    stringMetrics = metrics.stringifyJsonMetric(jsonMetrics)
    stringMetrics = metrics.addInternalMetrics(stringMetrics,start,end,1)
    assert stringMetrics == "jira_total_done{project_name=\"BIP\"} 42\njira_total_number_of_metrics 1\njira_total_execution_time_seconds 42\n"

# Asserts that liveness endpoints exist
@mock.patch('requests.request')
def test_alive(mock_request):
    response = metrics.alive(mock_request)
    assert response.status == 200
    response = metrics.ready(mock_request)

# Asserts that readyness endpoint exists and responds correctly
@mock.patch('requests.request')
def test_ready(mock_request):
    response = metrics.ready(mock_request)
    assert response.status == 503
    metrics.serviceIsReady = True
    response = metrics.ready(mock_request)
    assert response.status == 200
    


    