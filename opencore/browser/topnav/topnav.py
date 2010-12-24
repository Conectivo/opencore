"""
TopNav view classes.
"""
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.TeamSpace.permissions import ManageTeamMembership
from opencore.browser.base import BaseView
from opencore.browser.topnav.interfaces import ITopnavMenuItems
from opencore.i18n import _
from opencore.interfaces.message import ITransientMessage
from opencore.nui.contexthijack import HeaderHijackable
from opencore.content.page import OpenPage
from operator import itemgetter
from zope.component import getMultiAdapter

class TopNavView(HeaderHijackable):
    """
    Provides req'd information for rendering top nav in any context.
    """

    def contextmenu(self):
        """ask a viewlet manager for the context menu
           HeaderHijackable takes care of making sure that the context
           is set correctly if we are getting a request with certain
           headers set to specify the context"""
        manager = getMultiAdapter(
            (self.context, self.request, self),
            ITopnavMenuItems,
            name="opencore.topnavmenu")
        manager.update()
        return manager.render()

    @property
    def usermenu(self):
        if self.loggedin:
            viewname = 'topnav-auth-user-menu'
        else:
            viewname = 'topnav-anon-user-menu'
        view = getMultiAdapter((self.context, self.request), name=viewname)
        return view.__of__(aq_inner(self.context))


class AnonMenuView(BaseView):
    """
    View class for the user menu when user is anonymous.
    """
    @property
    def menudata(self):
        site_url = getToolByName(self.context, 'portal_url')()

        menudata = (

            {'content': _(u'Sign in'),
             'href': '%s/login' % site_url,
             },

            {'content': _(u'Create account'),
             'href': '%s/join' % site_url,
             },

            )

        return menudata


class AuthMenuView(BaseView):
    """
    View class for the user menu when user is logged in.
    """
    @property
    def user_message_count(self):
        """
        returns the number of transient messages currently stored
        for the logged in member
        """
        mem_id = self.loggedinmember.getId()
        tm = ITransientMessage(self.portal)
        t_msgs = tm.get_all_msgs(mem_id)
        msg_count = sum([len(value) for key,value in t_msgs.iteritems() if not key == 'Trackback'])

        query = dict(portal_type='OpenMembership',
                     getId=mem_id,
                     )
        mship_brains = self.catalog(**query)
        proj_invites = [brain for brain in mship_brains if brain.review_state == 'pending' and brain.lastWorkflowActor != mem_id]
        
        return msg_count + len(proj_invites)

    @property
    def menudata(self):
        mem_data = self.member_info
        site_url = getToolByName(self.context, 'portal_url')()
        menudata = (

            {'content': _(u'Sign out'),
             'href': '%s/logout' % site_url,
             },

            )

        return menudata
