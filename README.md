# leroncheung.github.io
Leroncheung's first python scraping copy from cookbook

import re # regular expression
re.findall(r'<td class="w2p_fw">(.*?)'</td>, html)
re.findall('''<tr id="places_area_row">.*?<tds*class=["']w2p_fw["']>(.*?)</td>''', html)

from bs4 import BeautifulSoup
html = download(url)
soup = BeautifulSoup(html, 'html.parse')
soup = BeautifulSoup(html, 'html5lib')
tr = soup.find(attrs={'id':'places_area_row'})
td = tr.find(attrs={'class':'w2p_fw'})
area = td.text

tree = fromstring(html)
td = tree.cssselect('tr#places_area_row > td.w2p_fw')[0]
area = td.text_content()


FIELDS = ('area', 'population', 'iso', 'country_or_district', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')

import re
def re_scraper(html):
    results = {}
    for field in FIELDS:
        results[field] = re.search('<tr id="places_%s_row">.*?<td class="w2p_fw">(.*?)</td>' % field, html).groups()[0]
    return results


from bs4 import BeautifulSoup
def bs_scraper(html):
    soup = BeautifulSoup(html, 'html_parse')
    results = {}
    for filed in FIELDS:
        results[filed] = soup.find('table').find('tr', id='places_%s_row' % filed).find('td', class_='w2p_fw').TEXT
    return results


from lxml.html import fromstring
def lxml_scraper(html):
    tree = fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.cssselect('table > tr#places_%s_row > td.w2p_fw' % field)[0].text_content()
    return results


def lxml_xpath_scraper(html):
    tree = fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.xpath('//tr[@id="places_%s_row"]/td[@class="w2p_fw"]' % field)[0].text_content()
    return results