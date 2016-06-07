import argparse, requests
import re
from urllib.request import urlopen
from urllib.parse import urljoin, urlsplit
from lxml import etree
import sys

aa = 0

def GET(url):
    response = requests.get(url)
    if response.headers.get('Content-Type', '').split(';')[0] != 'text/html':
        return
    text = response.text
    try:
        html = etree.HTML(text)
    except Exception as e:
        print('    {}: {}'.format(e.__class__.__name__, e))
        return
    links = html.findall('.//a[@href]')
    for link in links:
        yield GET, urljoin(url, link.attrib['href'])

def scrape(start, url_filter):
    global aa
    further_work = {start}
    already_seen = {start}
    while further_work:
        call_tuple = further_work.pop()
        function, url, *etc = call_tuple
        print(function.__name__, url, *etc)
        aa = aa+1
        res = requests.get(url)
        if res.headers.get('Content-Type', '').split(';')[0] != 'text/html':
	        continue
        text = res.text
        print(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",text))
        for call_tuple in function(url, *etc):
            if call_tuple in already_seen:
                continue
            already_seen.add(call_tuple)
            function, url, *etc = call_tuple
            if not url_filter(url):
                continue
            further_work.add(call_tuple)
        if aa == 150:
                sys.exit(0)

def main(GET):
    parser = argparse.ArgumentParser(description='Scrape a simple site.')
    parser.add_argument('url', help='the URL at which to begin')
    start_url = parser.parse_args().url
    starting_netloc = urlsplit(start_url).netloc
    url_filter = (lambda url: urlsplit(url).netloc == starting_netloc)
    scrape((GET, start_url), url_filter)

if __name__ == '__main__':
    main(GET)
