"""Functions for parsing Toronto Star articles."""

import urllib2
import bs4

def get_article_text(filepath):
    with open(filepath, 'r') as infile:
        page = infile.read()

    soup = bs4.BeautifulSoup(page)

    text_elems = soup.find_all("p", attrs={"itemprop": "articleBody"})
    text = " ".join(map(lambda elem: elem.get_text(), text_elems)).encode('utf-8')

    return text
