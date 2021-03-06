import unittest
from zope.app.component.hooks import setSite
from zope.testing import doctest
from opencore.testing.layer import OpencoreContent
from opencore.testing import dtfactory
from utils import UnescapeTests

optionflags = doctest.ELLIPSIS

import warnings; warnings.filterwarnings("ignore")

def test_suite():
    from Products.PloneTestCase import setup
    from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
    from pprint import pprint # imported because its passed via globs = locals()

    setup.setupPloneSite()
    def readme_setup(tc):
        tc._refreshSkinData()
        setSite(tc.portal)

    page_id = 'project-home'
    globs = locals()
    readme = dtfactory.ZopeDocFileSuite("README.txt",
                                        optionflags=optionflags,
                                        package='opencore.nui.wiki',
                                        test_class=FunctionalTestCase,
                                        globs = globs,
                                        setUp=readme_setup,
                                        layer = OpencoreContent
                                        )
    
    wikiadd = dtfactory.ZopeDocFileSuite("add.txt",
                                         optionflags=optionflags,
                                         package='opencore.nui.wiki',
                                         test_class=FunctionalTestCase,
                                         setUp=readme_setup,
                                         globs = globs,
                                         layer = OpencoreContent,
                                         )

    history = dtfactory.ZopeDocFileSuite("history.txt",
                                         optionflags=optionflags,
                                         package='opencore.nui.wiki',
                                         test_class=FunctionalTestCase,
                                         setUp=readme_setup,
                                         globs = globs,
                                         layer = OpencoreContent
                                         )

    htmldiff2 = doctest.DocFileSuite('test_htmldiff2.txt')

    return unittest.TestSuite((wikiadd, readme, history, htmldiff2, unittest.makeSuite(UnescapeTests)))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
