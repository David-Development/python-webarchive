from logging import CRITICAL, DEBUG, basicConfig, getLogger
from os import environ

# Make sure cssutils keeps quiet while parsing
import cssutils

cssutils.log.setLevel(CRITICAL)

# logfmt
basicConfig(format='level=%(levelname)s time="%(asctime)-15s" module="%(module)s" funcName="%(funcName)s" lineno=%(lineno)d message="%(message)s"', level=DEBUG)
log = getLogger()

USER_AGENT = environ.get(
    'USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30')
ACCEPT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate"
}
TARGET_URL = environ.get('TARGET_URL', 'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm')
ADDITIONAL_URLS = environ.get('ADDITIONAL_URLS', '')
OUTPUT_FILENAME = environ.get('OUTPUT_FILENAME', 'out.webarchive')
CONCURRENCY = int(environ.get('CONCURRENCY', '1'))
TIMEOUT = int(environ.get('TIMEOUT', '300'))
CHANGE_DOMAIN_FROM = environ.get('CHANGE_DOMAIN_FROM', '')
CHANGE_DOMAIN_TO   = environ.get('CHANGE_DOMAIN_TO', '')
