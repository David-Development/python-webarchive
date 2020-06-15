from asyncio import Queue, ensure_future, get_event_loop, wait_for
from cgi import parse_header
from urllib.parse import unquote, urldefrag, urljoin, urlparse

from aiohttp import ClientSession
from biplist import writePlist
from cssutils import getUrls, parseString
from lxml import html

from config import (ACCEPT_HEADERS, ADDITIONAL_URLS, CHANGE_DOMAIN_FROM,
                    CHANGE_DOMAIN_TO, CONCURRENCY, OUTPUT_FILENAME, TARGET_URL,
                    TIMEOUT, USER_AGENT, log)


async def crawler(client, url_queue, archive):
    while True:
        url = await url_queue.get()
        try:
            log.debug("Crawling url: {}".format(url))
            headers = ACCEPT_HEADERS
            headers['Referer'] = archive['top']
            response = await client.get(url, headers=headers)
            if response.status != 200:
                raise Exception("got response code other than 200 for url: {}".format(url))
            else:
                data = await response.read()
                content_type, params = parse_header(response.headers['content-type'])
                if CHANGE_DOMAIN_FROM and CHANGE_DOMAIN_TO:
                    wrUrl = url.replace(CHANGE_DOMAIN_FROM, CHANGE_DOMAIN_TO)
                else:
                    wrUrl = url
                item = {
                    "WebResourceData": data,
                    "WebResourceMIMEType": content_type,
                    "WebResourceURL": wrUrl
                }
                if 'charset' in params:
                    item['WebResourceTextEncodingName'] = params['charset']
                archive['items'].append(item)
        except Exception as exc:
            log.warn('Exception {}:'.format(exc), exc_info=True)

        finally:
            url_queue.task_done()


async def scrape(client, url, additionalUrls = []):
    tasks = []
    url_queue = Queue()

    archive = {
        'top': url,
        'items': []
    }
    await url_queue.put(url)

    for aUrl in additionalUrls:
        #print("adding additional url: " + aUrl)
        await url_queue.put(aUrl)
    #print(url_queue)

    def task_completed(future):
        exc = future.exception()
        if exc:
            log.error('Worker finished with error: {} '.format(exc), exc_info=True)

    for _ in range(CONCURRENCY):
        crawler_future = ensure_future(crawler(client, url_queue, archive))
        crawler_future.add_done_callback(task_completed)
        tasks.append(crawler_future)

    await wait_for(url_queue.join(), TIMEOUT)

    for task in tasks:
        task.cancel()

    await client.close()

    webarchive = {
        'WebMainResource': archive['items'].pop(0),
        'WebSubresources': archive['items']
    }

    writePlist(webarchive, OUTPUT_FILENAME)


if __name__ == '__main__':
    client = ClientSession()
    loop = get_event_loop()
    #additionalUrls = ADDITIONAL_URLS.split(";")
    additionalUrls = list(filter(None, ADDITIONAL_URLS.split(";"))) # remove empty urls from list
    loop.run_until_complete(scrape(client, TARGET_URL, additionalUrls))
