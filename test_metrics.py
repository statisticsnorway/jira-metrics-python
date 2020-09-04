import logging.config
import configparser
import metrics
from datetime import datetime
import urllib.request
from unittest import mock
from requests import request
from aiohttp.web import Response
from jiracollector import JiraCollector
import pytest


config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)

logger = logging.getLogger()

# Asserts that "happy-path" works, i.e the returned metrics from JiraCollector
# is correctly converted and internal metrics are added to the cached metrics
@mock.patch('jiracollector.JiraCollector.__init__',mock.Mock(return_value=None))
@mock.patch('jiracollector.JiraCollector.collect')
def test_collect_metrics(mock_collector):
    metrics_dict = {
        "jira_total_done{project_name=\"BIP\"}":"42"
    }
    mock_collector.return_value = metrics_dict

    metrics.serviceIsReady = False
    metrics.collectJiraMetrics()
    assert metrics.serviceIsReady == True
    assert metrics.cachedMetrics == "jira_total_done{project_name=\"BIP\"} 42\njira_total_number_of_metrics 1\njira_total_execution_time_seconds 0\n"

# Asserts that an exception is raised if init or collect from Jiracollector raises an exception
@mock.patch('jiracollector.JiraCollector.__init__',side_effect=mock.Mock(side_effect=Exception("Just for testing exception Exception")),
)
def test_collect_metrics_raises_exception_if_exception_from_jiracollector(mock_collector):
    metrics.serviceIsReady = False
    with pytest.raises(Exception):
        metrics.collectJiraMetrics()

@mock.patch('requests.request')
def test_alive_always_returns_200(mock_request):
    response = metrics.alive(mock_request)
    assert response.status == 200

@mock.patch('requests.request')
def test_ready_returns_503_or_200_depending_on_serviceIsReady(mock_request):
    response = metrics.ready(mock_request)
    assert response.status == 503
    metrics.serviceIsReady = True
    response = metrics.ready(mock_request)
    assert response.status == 200
