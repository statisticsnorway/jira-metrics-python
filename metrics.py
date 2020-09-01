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

    start = datetime.now()
    logger.info('Start collecting metrics...')
    jiraCollector = JiraCollector(config.get('jira','metrics_descriptions_file'))
    metricsDict = jiraCollector.collect()
 
    logger.info("Converting metrics to strings")
    metricsStr = str(metricsDict)
    metricsStrReplaced = metricsStr[1:-1].replace("'", "").replace(':', '').replace(",", "\n").replace(" j", "j") + "\n"
    end = datetime.now()    

    # Log and add metrics for this application
    logger.info("Adding metrics for this application")
    totalExecutionTime = abs((end - start).seconds)
    totalNumberOfMetrics = len(metricsDict)
    metricsStrReplaced = metricsStrReplaced+"jira_total_number_of_metrics "+str(totalNumberOfMetrics)+"\n"
    metricsStrReplaced = metricsStrReplaced+"jira_total_execution_time_seconds "+str(totalExecutionTime)+"\n"
    
    # Update cached metrics
    cachedMetrics = metricsStrReplaced
    logger.info("% d metrics collected OK in %d seconds",totalNumberOfMetrics,totalExecutionTime)
    
    serviceIsReady = True


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


if __name__ == "__main__":
    logger.info("Starting app")
    # Create a background thread to collect metrics in a "cache"
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(collectJiraMetrics, 'interval', minutes=config.getint('runtime_config','minutes_between_metrics_collection'), max_instances=1, next_run_time=datetime.now())
    scheduler.start()

    # Create a webapp to serve cached metrics on / endpoint
    app = web.Application()
    app.router.add_get('/', metrics)
    app.router.add_get('/health/ready', ready)
    app.router.add_get('/health/alive', alive)

    web.run_app(app)
