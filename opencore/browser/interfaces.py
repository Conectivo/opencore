"""
Forms, skins etc

General architecture interfaces go in opencore.interfaces
"""
from zope.interface import Interface, Attribute, implements
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import ASCIILine, TextLine, List, Bool
from zope.i18nmessageid import MessageFactory


class IOpenPlansSkin(IDefaultBrowserLayer):
    """Skin for OpenPlans"""


class IAddOpenPlans(Interface):
    """Add form for topp site"""

    id = ASCIILine(
        title=u"Id",
        description=u"The object id.",
        default='openplans',
        required=True
        )
    
    title = TextLine(
        title=u"Title",
        description=u"Name of the site instance",
        default=u"OpenPlans",
        required=True
        )

    testcontent = Bool(
        title=u"Create test content",
        description=u"Please create example projects and members",
        default=False,
        required=False
        )