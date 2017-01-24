"""Functions for scraping Toronto Star articles"""

import urllib2
#import re
import bs4

BASE_URL = "http://www.thestar.com"
BASE_SEARCH_URL = BASE_URL + "/search.html?q="
RESULTS_PER_PAGE = 20

def get_search_result_links(search_str):
    print "Searching for \"%s\"" % search_str
    base_url_search = BASE_SEARCH_URL + search_str.replace(" ", "+") + "&pagenum="

    # Get total number of results
    page = urllib2.urlopen(base_url_search + "1").read()
    soup = bs4.BeautifulSoup(page)
    
    # FOR OLD HTML
    #match = re.search("[0-9]+\sto\s[0-9]+\sof\s([0-9]+)\sresults", page)
    #if not match:
    #    raise ValueError
    #total_results = int(match.group(1))

    div_tag = soup.find("div", "search-parent__results-count")
    span_elems = div_tag.find_all("span")
    total_results = 0
    for span_elem in span_elems:
        try:
            num = int(span_elem.get_text())
        except ValueError:
            continue
        if num > total_results:
            total_results = num

    print "%d results" % total_results

    # Get links to all results
    links = []
    
    result_start_num = 1
    while result_start_num < total_results:
        url = base_url_search + str(result_start_num)
        print "Parsing %s for links" % url
        page = urllib2.urlopen(url).read()
        soup = bs4.BeautifulSoup(page)
    
        # FOR OLD HTML
        #elems = soup.find_all("p", "headline")
        #for elem in elems:
        #    a_tag = elem.find("a")
        #    link = a_tag["href"]
        #    links.append(link)

        story_body_tags = soup.find_all("div", "story__body")
        for story_body_tag in story_body_tags:
            a_tag = story_body_tag.find("a")
            link = a_tag["href"]
            links.append(BASE_URL + link)
    
        result_start_num += RESULTS_PER_PAGE

    return links

def get_article_text(url):
    page = urllib2.urlopen(url).read()
    soup = bs4.BeautifulSoup(page)

    text_elems = soup.find_all("div", class_="text combinedtext parbase section")
    text = " ".join(map(lambda elem: elem.get_text(), text_elems)).encode('utf-8')

    return text
