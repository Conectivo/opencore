import os, sys, unittest
from zope.testing import doctest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase 
from Testing.ZopeTestCase import FunctionalDocFileSuite
from opencore.testing.layer import OpencoreContent
from Products.OpenPlans.tests.openplanstestcase import OpenPlansTestCase
from opencore.tasktracker.tests import MockTaskTrackerHTTPwithContent

#optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
optionflags = doctest.ELLIPSIS

import warnings; warnings.filterwarnings("ignore")

def test_suite():
    from Products.Five.utilities.marker import erase as noLongerProvides
    from Products.PloneTestCase import setup
    from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
    from Products.CMFCore.utils import getToolByName
    from Testing.ZopeTestCase import FunctionalDocFileSuite, installProduct
    from pprint import pprint
    from zope.interface import alsoProvides
    from Products.OpenPlans.interfaces import IReadWorkflowPolicySupport
    from opencore.testing import utils
    from opencore.nui.indexing import authenticated_memberid

    def contents_content(tc):
        tc.loginAsPortalOwner()
        proj = tc.portal.projects.p2
        proj.invokeFactory('Document', 'new1', title='new title')
        proj.invokeFactory('Image', 'img1', title='new image')
        proj.restrictedTraverse('project-home').invokeFactory('FileAttachment', 'fa1', title='new file')
        proj.invokeFactory('Folder', 'lists', title='Listen Stub')
        proj.lists.invokeFactory('Document', 'list1', title='new list')
        proj.lists.list1.portal_type = "Open Mailing List"
        proj.lists.list1.reindexObject()

    def readme_setup(tc):
        tc._refreshSkinData()

    def metadata_setup(tc):
        tc.project = tc.portal.projects.p1
        tc.page = getattr(tc.project, 'project-home')

    globs = locals()
    readme = FunctionalDocFileSuite("README.txt", 
                                    optionflags=optionflags,
                                    package='opencore.nui.project',
                                    test_class=FunctionalTestCase,
                                    globs = globs,
                                    setUp=readme_setup
                                    )
    
    metadata = FunctionalDocFileSuite("metadata.txt", 
                                    optionflags=optionflags,
                                    package='opencore.nui.project',
                                    test_class=FunctionalTestCase,
                                    globs = globs,
                                    setUp=metadata_setup
                                    )
    
    contents = FunctionalDocFileSuite("contents.txt",
                                    optionflags=optionflags,
                                    package='opencore.nui.project',
                                    test_class=OpenPlansTestCase,
                                    globs = globs,
                                    setUp=contents_content, 
                                    )

    manage_team = FunctionalDocFileSuite("manage-team.txt",
                                         optionflags=optionflags,
                                         package='opencore.nui.project',
                                         test_class=OpenPlansTestCase,
                                         globs = globs, 
                                         )

    suites = (contents, metadata, manage_team)
    for suite in suites:
        suite.layer = OpencoreContent
    readme.layer = MockTaskTrackerHTTPwithContent

    return unittest.TestSuite(suites + (readme,))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
