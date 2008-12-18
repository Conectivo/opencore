'''
Custom namespace to be used in TALES expressions, like eg.
 tal:content="somedate/opencore:pretty_data"

See http://wiki.zope.org/zope3/talesns.html
and http://www.openplans.org/projects/opencore/how-to-create-a-tales-namespace
'''

from Products.CMFCore.utils import getToolByName
from opencore.project.utils import project_noun
from topp.utils.pretty_date import prettyDate
from zope import component
from zope import interface
from zope.app.component.hooks import getSite
from zope.traversing.interfaces import IPathAdapter


# XXX THIS DOES NOT WORK IN VIEWS CALLED FROM UNIT TESTS
# ... see http://permalink.gmane.org/gmane.comp.web.zope.general/61538
# and http://www.openplans.org/projects/opencore/lists/opencore-dev/archive/2008/12/1229475623696/forum_view
# Until that's fixed, we can't really use this namespace.

class OpencoreTales(object):
    component.adapts(interface.Interface)
    interface.implements(IPathAdapter)

    def __init__(self, context):
        if callable(context):
            # XXX Are we sure we want to implicitly call here?
            # This can easily lead to infinite recursion, eg. if our
            # TALES expression is used in the default view on a
            # context, because calling the object invokes the default
            # view again.
            self.context = context()
        else:
            self.context = context

    def pretty_date(self):
        return prettyDate(self.context)

    def project_noun(self):
        return project_noun()

    def member_title(self):
        return member_title(self.context)
        

def member_title(id_or_dict):
    """
    Get member fullname, falling back to ID if no fullname is set.
    """
    # Backported from sputnik.utils.
    if isinstance(id_or_dict, dict):
        # No need to do all those lookups.
        return id_or_dict['fullname'].strip() or id_or_dict['id']
    if not isinstance(id_or_dict, basestring):
        raise TypeError('member_title expected a string id or '
                        'memberdata dict as context, got %s'
                        % str(id_or_dict))
    id = id_or_dict
    context = getSite()
    pid = getToolByName(context, 'portal_url').getPortalObject().id
    mt = getToolByName(context, 'membrane_tool')
    try:
        meta = mt.getMetadataForUID('/%s/portal_memberdata/%s' % (pid, id))
        return meta['Title']
    except KeyError:
        #if not in the catalog, fall back on the member id
        return id