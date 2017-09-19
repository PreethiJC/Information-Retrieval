"""
 Written by Vinod Vishwanath
 as part of Information Retrieval
 - Summer 1 2017
 - Northeastern University
"""
from urllib.parse import urlparse


class Canonicalizer:

    @staticmethod
    def get_domain(url, include_scheme=True):

        parse = urlparse(url)
        parse = parse._replace(scheme='http')
        scheme = parse.scheme.lower()
        domain = parse.netloc.lower()
        clean_domain = Canonicalizer.clean_domain(domain, scheme=scheme)

        if include_scheme:
            return scheme + '://' + clean_domain
        else:
            return domain

    @staticmethod
    def is_relative_url(url):

        parse = urlparse(url)

        return parse.netloc == ''

    @staticmethod
    def canonicalize(url, domain=None):

        if domain is not None:
            url = domain.strip('/') + '/' + url

        parse = urlparse(url)
        output = ''
        parse = parse._replace(scheme='http')
        output += parse.scheme.lower() + '://'
        output += Canonicalizer.clean_domain(parse.netloc.lower(),
                                             parse.scheme.lower())
        if len(parse.path) > 0:
            output += Canonicalizer.clean_path(parse.path)

        return output

    @staticmethod
    def clean_domain(domain, scheme):

        if scheme == 'http':
            return rchop(domain, ':80')
        elif scheme == 'https':
            return rchop(domain, ':443')

        return domain

    @staticmethod
    def clean_path(path):

        comps = path.split('/')
        output = ''
        for cmp in comps:

            if len(cmp) > 0 and cmp != '/':
                output += '/' + cmp

        return output

def rchop(string, ending):

    if string.endswith(ending):
        return string[:-len(ending)]
    return string


print(Canonicalizer.get_domain("https://www.en.wikipedia.org/wiki/World_War_II"))