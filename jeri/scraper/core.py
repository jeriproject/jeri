"""Shared library for article scraping."""

import urllib2
import os

def download_articles(urls, get_article_text_func, output_dir="./"):
    for url in urls:
        text = get_article_text_func(url)
        filename = url.split("/")[-1]
        filepath = os.path.join(output_dir, filename)
        print filepath
        with open(filepath, 'w') as output:
            output.write(text)

def download_html_files(urls, output_dir="./"):
    n = 0
    for url in urls:
        n += 1
        print n
        html = urllib2.urlopen(url).read()
        filename = url.split("/")[-1]
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        filepath = os.path.join(output_dir, filename)
        print filepath
        with open(filepath, 'w') as output:
            output.write(html)
