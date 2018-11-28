import urllib.request
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urljoin
from urllib import robotparser
from urllib.parse import urlparse
import re   # reglar expression
import itertools
import time
import csv
from lxml.html import fromstring

# WSWP:Web Scraping Witch Python
def download(url, user_agent = 'wswp', num_retries = 2, charset = 'utf-8', proxy = None):
    """
        Use user-agent to download website pages and return HTML TEXT, and will try a few times after website return 5** error code
        return urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8')
    """
    print('Downloading:', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)    #用户代理下载网页
    try:
        if proxy:
            proxy_support = urllib.request.ProxyHandler({'http': proxy})    #代理访问页面
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        # Decode by utf-8
        html = resp.read().decode(cs)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retries - 1)
    return html

def crawl_sitemap(url):
    """
        Download the sitemap file and extract the sitemap links, download each link
        eg: http://example.python-scraping.com/sitemap.xml
        links = re.findall('<loc>(.*?)</loc>', download(url))
    """
    sitemap = download(url)
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    for link in links:
        html = download(link)
        print(html) # To anylyse html page's contents

def crawl_site(url, max_errors = 5):
    """
        Use ID in database to download all countries' pages
        eg: http://example.python-scraping.com/view/Afghanistan-1
        eg: http://example.python-scraping.com/view/Aland-Islands-2
        eg: http://example.python-scraping.com/view/Albania-3
    """
    num_errors = 0
    for page in itertools.count(1):
        pg_url = '{}{}'.format(url, page)
        html = download(pg_url)
        if html is None:
            num_errors += 1
            if num_errors == max_errors:
                break
        else:
            print(html) # To anylyse html page's contents

def link_crawler(start_url, link_regex, robots_url = None, user_agent = 'wswp', max_depth = 4):
    """
        Crawl from the given start URL and crawl following links matched by link_regex in the html pages
        eg: link_regex = '/(index|view)/'
        eg: http://example.python-scraping.com/view/index/1
        eg: http://example.python-scraping.com/view/Afghanistan-1
    """
    if not robots_url:
        robots_url = '{}/robots.txt'.format(start_url)
    rp = get_robots_parser(robots_url)
    crawl_queue = [start_url]
    seen = {}
    while crawl_queue:
        url = crawl_queue.pop()
        # Check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print('Skiping %s due to depth ' % url)
                continue
            html = download(url, user_agent = user_agent)
            if not html:
                continue
            # Filter for links matching our regular expression
            for link in get_links(html):
                if re.match(link_regex, link):  # Effective links
                    abs_link = urljoin(start_url, link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1  # Note the depth of pages which have been seen 
                        crawl_queue.append(link)
        else:
            print('Blocked by robots.txt: ', url)

def get_links(html):
    """
        Return a list of links from html pages
    """
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?["'])""", re.IGNORECASE)
    return webpage_regex.findall(html)

def get_robots_parser(robots_url):
    """
        retrun the robots parser object using the robots_url
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp

class Throttle:
    """
        Add a delay between downloads for each domain in case that the websites add the IP into blacklist
    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}
    
    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (time.time() - last_accessed)
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = time.time()

class CsvCallback:
    def __init__(self):
        self.writer = csv.writer(open('../data/countries_or_distritcs.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country_or_district', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = fromstring(html)
            all_rows = [tree.xpath('//tr[@id="places_%s_row"]/td[@class="w2p_fw"]' % field)[0].text_content() for field in self.fields]
            self.writer.writerow(all_rows)