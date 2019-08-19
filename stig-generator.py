from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from lxml.html.clean import clean_html
from httplib2 import Http
import logging

# Set up logging
logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class STIGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stig_links, self.json_files = [], []
        self.base_url = "https://www.stigviewer.com"
        self.first_run = True

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if self.first_run:
                if attr[1] is not None and attr[1][0:6] == "/stig/":
                    logger.info(str(self.base_url + attr[1]) + " was added")
                    self.stig_links.append(self.base_url + attr[1])
            else:
                if attr[1] is not None and attr[1][-5:0] == "/json":
                    logger.info(str(self.base_url + attr[1]) + " was added")
                    self.json_files.append(self.base_url + attr[1])

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

stig_html= urlopen("https://www.stigviewer.com/stigs").read().decode('utf-8', 'ignore')

stig_parser = STIGParser()
stig_parser.feed(clean_html(stig_html))
stig_parser.first_run = False
# Remove strange link that I can't access in loop
stig_parser.stig_links.remove("https://www.stigviewer.com/stig/symantec_antivirus_managed_client/")

h = Http()
for link in stig_parser.stig_links:
    response = h.request(link, "HEAD")[0]
    if response.status == 200:
        logger.info("Successfully reached {}".format(link))
    else:
        logger.info("Failed! {} does not exist. Removing.".format(link))
        stig_parser.stig_links.remove(link)

for link in stig_parser.stig_links:
    logger.info(link + " is being added")
    json_html = urlopen(link).read().decode('utf-8', 'ignore')

    stig_parser.feed(clean_html(json_html))
