import asyncio
import logging
import json
from aiohttp import web
from aiocache import cached
from aiocache.serializers import JsonSerializer
from jiracollector import JiraCollector


@cached(ttl=45, key="function_key", serializer=JsonSerializer())
async def getJiraCollector():
    jiraCollector = JiraCollector()
    return jiraCollector.collect()


async def metrics(request):
    metricsDict = await getJiraCollector()
    metricsStr = str(metricsDict)
    metricsStrReplaced = metricsStr[1:-1].replace("'", "").replace(':', '').replace(",", "\n").replace(" j", "j") + "\n"
    return web.Response(text=metricsStrReplaced)


# It is also possible to cache the whole route, but for this you will need to
# override `cached.get_from_cache` and regenerate the response since aiohttp
# forbids reusing responses
class CachedOverride(cached):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_from_cache(self, key):
        try:
            value = await self.cache.get(key)
            if type(value) == web.Response:
                return web.Response(
                    body=value.body,
                    status=value.status,
                    reason=value.reason,
                    headers=value.headers,
                )
            return value
        except Exception:
            logging.exception("Couldn't retrieve %s, unexpected error", key)

def alive(request):
    return web.Response(status=200, text="OK")

def ready(request):
    ready = True
    if ready:
        return web.Response(status=200, text="OK")
    else:
        return web.Response(status=503, text="Not ready yet")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', metrics)
    app.router.add_get('/health/ready', ready)
    app.router.add_get('/health/alive', ready)

    web.run_app(app)