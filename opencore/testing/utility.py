from minimock import HTTPMock
from minimock import Mock
from opencore.testing import alsoProvides
from opencore.utility.interfaces import IHTTPClient
from zope.component import provideUtility

def mock_utility(name, provides, cls=Mock):
    """
    a mock utility factory
    """
    utility = cls(name)
    utility.__provides__=None
    alsoProvides(utility, provides)
    return utility

def setup_mock_http():
    http = mock_utility('httplib2.Http', IHTTPClient, cls=HTTPMock)
    provideUtility(http, provides=IHTTPClient)



