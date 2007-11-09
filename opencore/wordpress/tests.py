import os, sys, unittest
from zope.testing import doctest
from collective.testing import utils
from zope.testing import doctestunit
from zope.testing import doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from zope.interface import alsoProvides
from zope.testing.cleanup import cleanUp
from opencore.testing.layer import MockHTTPWithContent

def clean_CA(tc):
    return cleanUp()

import warnings; warnings.filterwarnings("ignore")

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

def readme_setup(tc):
    tc.new_request = utils.new_request()
    import opencore.wordpress
    zcml.load_config('test-directive.zcml', opencore.wordpress)
    from zope.app.annotation.interfaces import IAttributeAnnotatable
    from zope.testing.loggingsupport import InstalledHandler
    tc.log = InstalledHandler(opencore.wordpress.LOG)

def directive_setup(tc):
    import opencore.wordpress
    zcml.load_config('test-directive.zcml', opencore.wordpress)

def test_suite():
    from zope.component import getMultiAdapter, getUtility
    from opencore.testing import * # star imports are for pansies
    from opencore.utility.interfaces import IHTTPClient
    
    directive = doctest.DocFileSuite('directive.txt',
                                     package='opencore.wordpress',
                                     optionflags=optionflags,
                                     setUp=directive_setup,
                                     tearDown=clean_CA,
                                     globs=locals())
    unit_suites = (directive, )
    
    readme = ztc.FunctionalDocFileSuite('README.txt',
                                        package='opencore.wordpress',
                                        optionflags=optionflags,
                                        setUp=readme_setup,
                                        globs=locals())
    
    zcml_suites = (readme,)
    for suite in zcml_suites:
        suite.layer = MockHTTPWithContent
        
    suites = unit_suites + zcml_suites
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
