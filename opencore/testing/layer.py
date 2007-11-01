from Products.CMFCore.utils  import getToolByName
from Products.Five import pythonproducts
from Products.OpenPlans.tests.utils import installConfiguredProducts
from Products.PloneTestCase.layer import PloneSite, ZCML
from Products.PloneTestCase.setup import setupPloneSite
from Testing import ZopeTestCase
from opencore.project.handler import add_redirection_hooks 
from opencore.testing.utility import setup_mock_http
from utils import get_portal, get_portal_as_owner, create_test_content
from topp.utils.testing import layer_factory
from topp.utils import introspection
import random
import transaction as txn


class MailHostMock(object):
    """
    mock up the send method so that emails do not actually get sent
    during automated tests
    """
    def __init__(self):
        self.messages = []
    def send(self, msg, mto=None, mfrom=None, subject=None):
        msg = {'msg': msg,
               'mto': mto,
               'mfrom': mfrom,
               'subject': subject,
               }
        self.messages.append(msg)
    secureSend = send
    def validateSingleEmailAddress(self, email):
        return True


class BrowserIdManagerMock(object):
    """
    mock a browser_id_manager at the Zope root.
    """
    def __init__(self):
        self.same = True
        self._same_id = '111111111111'

    def getBrowserId(self, create=False):
        if self.same:
            return self._same_id
        else:
            return str(random.random())


class SiteSetupLayer(PloneSite):
    installConfiguredProducts()
    setupPloneSite()

    @classmethod
    def setUp(cls):
        portal = get_portal()
        setup_tool = portal.portal_setup
        setup_tool.setImportContext('profile-membrane:default')
        setup_tool.runAllImportSteps()

        setup_tool.setImportContext('profile-remember:default')
        setup_tool.runAllImportSteps()

        # install OpenPlans into ZTC
        ZopeTestCase.installProduct('OpenPlans')

        txn.commit()

    @classmethod
    def tearDown(cls):
        raise NotImplementedError


class OpenPlansLayer(SiteSetupLayer):
    @classmethod
    def setUp(cls):
        # need to explicitly apply pythonproducts patches to get the
        # borg.localrole package's FactoryDispatcher to work
        pythonproducts.applyPatches()
        portal = get_portal_as_owner()
        qi = getToolByName(portal, 'portal_quickinstaller')
        qi.installProduct('OpenPlans')
        portal.clearCurrentSkin()

        portal.oldMailHost = portal.MailHost
        portal.MailHost = MailHostMock()

        portal.browser_id_manager = BrowserIdManagerMock()
        txn.commit()

    @classmethod
    def tearDown(cls):
        portal = get_portal_as_owner()
        del portal.MailHost
        portal.MailHost = portal.oldMailHost
        del portal.oldMailHost
        del portal.browser_id_manager


class OpencoreContent(OpenPlansLayer):
    @classmethod
    def setUp(cls):
        portal = get_portal_as_owner()
        create_test_content(portal)
        add_redirection_hooks(portal.projects)
        txn.commit()

    @classmethod
    def tearDown(cls):
        raise NotImplementedError

OpenCoreContent = OpencoreContent


class MockHTTP(ZCML):
    @classmethod
    def setUp(cls):
        setup_mock_http()

    @classmethod
    def tearDown(cls):
        raise NotImplementedError


class MockHTTPWithContent(OpencoreContent):
    """
    Add the mock httplib2 utility to the OpencoreContent layer.
    """
    @classmethod
    def setUp(cls):
        setup_mock_http()
        txn.commit()
    
    @classmethod
    def tearDown(cls):
        raise NotImplementedError


