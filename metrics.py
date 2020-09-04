import asyncio
import logging
import json
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from aiohttp import web
from jiracollector import JiraCollector
from datetime import datetime
from pythonjsonlogger import jsonlogger
import logging.config
import configparser

config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)

logger = logging.getLogger()

cachedMetrics = ""
serviceIsReady = False

# Collects metrics from Jira
def collectJiraMetrics():
    global cachedMetrics
    global serviceIsReady
    #metricsStrReplaced =""

    start = datetime.now()
    logger.info('Start collecting metrics...')
    metrics_descriptions_file = config.get('jira','metrics_descriptions_file')
    try:
        jiraCollector = JiraCollector(metrics_descriptions_file)
        # Collect all jira metrics
        metricsDict = jiraCollector.collect()
    except:
        logger.exception("Error while trying to collect metrics")
        raise

    # Convert to metric format
    metricsStr = stringifyJsonMetric(str(metricsDict))
    end = datetime.now()    

    # Add metrics about this run
    metricsStr = addInternalMetrics(metricsStr, start,end,len(metricsDict))

    # Update cached metrics
    cachedMetrics = metricsStr
    logger.info("Metrics collected OK")
    
    serviceIsReady = True

def stringifyJsonMetric(jsonMetrics):
    logger.info("Converting metrics to strings")
    metricsStrReplaced = jsonMetrics[1:-1].replace("'", "").replace(':', '').replace(",", "\n").replace(" j", "j") + "\n"
    return metricsStrReplaced

def addInternalMetrics(strMetrics, startTime, endTime, numberOfMetricsCollected):
# Log and add metrics for this application
    logger.info("Adding metrics for this application")
    totalExecutionTime = abs((endTime - startTime).seconds)
    strMetrics = strMetrics+"jira_total_number_of_metrics "+str(numberOfMetricsCollected)+"\n"
    strMetrics = strMetrics+"jira_total_execution_time_seconds "+str(totalExecutionTime)+"\n"
    return strMetrics


# Serves the cached metrics at /
def metrics(request):
    logger.info('Retrieving cached metrics')
    global cachedMetrics
    return web.Response(text=cachedMetrics)

# Liveness
def alive(request):
    return web.Response(status=200, text="OK")

# Readiness
def ready(request):
    global serviceIsReady
    if serviceIsReady:
        return web.Response(status=200, text="OK")
    else:
        return web.Response(status=503, text="Not ready yet")

# Create a background scheduler for collecting metrics
def createBackgroundScheduler():
    logger.info("Starting background scheduler")
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(collectJiraMetrics, 'interval', minutes=config.getint('runtime_config','minutes_between_metrics_collection'), max_instances=1, next_run_time=datetime.now())
    scheduler.start()

# Entrypoint
if __name__ == "__main__":
    createBackgroundScheduler()
    # Create a webapp to serve cached metrics on / endpoint
    app = web.Application()
    app.router.add_get('/', metrics)
    app.router.add_get('/health/ready', ready)
    app.router.add_get('/health/alive', alive)

    web.run_app(app)