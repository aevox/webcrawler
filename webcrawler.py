#!/usr/bin/env python

import sys
import lxml.html
import urllib
import urlparse
from httplib2 import iri2uri
from os.path import splitext


class Crawler():
    '''HTTP Crawling and reporting.'''

    def __init__(self, url=str()):
        self.url = url

    def get_links(self, url=None, opt=None):
        '''
        Return a dict(tag, value) of links from a webpage,
        opt is the tag you want to filter.
        example : "opt = 'a'" will return all the 'a' tags.
        '''
        links = {}
        url = iri2uri(url)
        html_stream = urllib.urlopen(url)
        html_string = html_stream.read()
        html_stream.close()
        lxml_web_page = lxml.html.fromstring(html_string)
        # transform all the urls in absolute urls
        for elem, attr, link, pos in lxml_web_page.iterlinks():
            absolute = urlparse.urljoin(url, link.strip())
            if elem.tag in links:
                links[elem.tag].append(absolute)
            else:
                links[elem.tag] = [absolute]
        if opt is None:
            list_links = []
            for tag, tag_links in links.iteritems():
                for tag_link in tag_links:
                    list_links.append(tag_link)
            return list(set(list_links))
        else:
            links_opt = []
            try:
                links_opt = list(set(links[opt]))
            # No links with the tag 'opt'
            except KeyError:
                pass
            return links_opt

    def filter_links_ext(self, links=[], extensions=[]):
        '''
        Filters a list of links and returns a list
        containing only urls with input extensions.
        '''
        url_filtered = []
        for link in links:
            url_path = urlparse.urlparse(link).path
            extension = splitext(url_path)[1]
            if extension in extensions:
                url_filtered.append(link)
        return url_filtered

    def crawl(self, opt=None, extensions=None):
        '''
        Returns a dict(url, urls[]) where urls are links
        with a tag defined by 'opt'
        '''
        links_to_crawl = self.get_links(self.url, 'a')
        result = []
        result += self.get_links(self.url, opt)
        for link in links_to_crawl:
            try:
                result += self.get_links(link, opt)
            # IOError are raised if one of the url isn't one.
            # KeyError is raised if there is no tag 'opt'
            except (IOError, KeyError):
                continue
        result = list(set(result))
        if extensions:
            result = self.filter_links_ext(result, extensions)
        return result


if __name__ == '__main__':
    results = {}
    for url in sys.stdin:
        image_crawler = Crawler(url.strip())
        results[url] = image_crawler.crawl('img', ['.jpg', '.png', '.gif'])
    print results
