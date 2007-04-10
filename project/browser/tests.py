import os, sys, unittest
from zope.testing import doctest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase 
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.OpenPlans.tests.openplanstestcase import OpenPlansLayer

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

import warnings; warnings.filterwarnings("ignore")

def test_suite():
    from Testing.ZopeTestCase import FunctionalDocFileSuite, installProduct
    from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
    from Products.PloneTestCase import setup
    from opencore.testing import alsoProvides, noLongerProvides, create_test_content
    from opencore import redirect

    setup.setupPloneSite()
    def readme_setup(tc):
        create_test_content(tc.portal)
        tc._refreshSkinData()

    globs = locals()
    readme = FunctionalDocFileSuite("README.txt",
                                    optionflags=optionflags,
                                    package='opencore.project.browser',
                                    test_class=FunctionalTestCase,
                                    globs = globs,
                                    setUp=readme_setup
                                    )

    readme.layer = OpenPlansLayer

    return unittest.TestSuite((readme,))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
