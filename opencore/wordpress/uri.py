"""
utility, directive and helper functions for locating the active
wordpress instance
"""
from opencore.wordpress.interfaces import IWordpressInfo
from zope.interface import implements
from zope.component import getUtility

class WordpressURI(object):
    implements(IWordpressInfo)
    def __init__(self, uri=None, external_uri=None):
        self.uri = uri
        self.external_uri = external_uri

_wp_info = WordpressURI()

def set_wp_info(uri, external_uri=None):
    _wp_info.uri=uri
    _wp_info.external_uri = external_uri

def configure_wp_info(_context, uri, external_uri=None):
    _context.action(
        # if more than one WP_info is registered, will raise conflict
        # warning. can be overridden after configuration
        discriminator = 'opencore.wordpress.wp_info already registered',
        callable = set_wp_info,
        args = (uri, external_uri,)
        )

def get():
    return getUtility(IWordpressInfo).uri

def get_external_uri():
    return getUtility(IWordpressInfo).external_uri
