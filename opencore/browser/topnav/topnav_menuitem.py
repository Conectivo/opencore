from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from opencore.interfaces import IMemberFolder
from opencore.interfaces import IProject
from opencore.interfaces import IOpenPage
from opencore.interfaces.adding import IAddProject
from opencore.interfaces.adding import IAmAPeopleFolder
from zope.interface import implements
from zope.interface import Interface
from Products.Five.viewlet.viewlet import ViewletBase
from Acquisition import Explicit


class BaseMenuItem(ViewletBase):
    render = ZopeTwoPageTemplateFile('topnav_menuitem.pt')

# class BaseMemberMenuItem(ContextProvidedMixin, BaseMenuItem):
#     should_be_provided = IMemberFolder

# class PortalContextMenuItem(BaseMenuItem):
#     folder_context = None

#     def context_matches(self):
#         # matching is handled by configuration here
#         return True

#     def get_url(self):
#         portal = getToolByName(self.context, 'portal_url').getPortalObject()
#         return getattr(portal, self.folder_context).absolute_url()

# # Member menu items
# class MemberWikiMenuItem(BaseMemberMenuItem):
#     name = u'Wiki'

#     def get_url(self):
#         mem = self._item_providing(self.should_be_provided)
#         return '%s/%s-home' % (mem.absolute_url(), mem.getId())

#     def is_selected(self):
#         return IOpenPage.providedBy(self.context)

# class ProfileMenuItem(BaseMemberMenuItem):
#     name = u'Profile'
#     item_url = 'profile'

# class AccountMenuItem(BaseMemberMenuItem):
#     name = u'Account'
#     item_url = 'account'

# # Project menu items
# class ProjectWikiMenuItem(BaseProjectMenuItem):
#     name = u'Wiki'

#     def get_url(self):
#         item = self._item_providing(self.should_be_provided)
#         return '%s/project-home' % item.absolute_url()

#     def is_selected(self):
#         return IOpenPage.providedBy(self.context)

# class TeamMenuItem(BaseProjectMenuItem):
#     name = u'Team'
#     item_url = 'team'

# class ManageTeamMenuItem(BaseProjectMenuItem):
#     name = u'Manage Team'
#     item_url = 'manage-team'

# class ContentsMenuItem(BaseProjectMenuItem):
#     name = u'Contents'
#     item_url = 'contents'

# class PreferencesMenuItem(BaseProjectMenuItem):
#     name = u'Preferences'
#     item_url = 'preferences'

# class JoinMenuItem(BaseProjectMenuItem):
#     name = u'Join Project'
#     item_url = 'request-membership'

#     def context_matches(self):
#         if not super(JoinMenuItem, self).context_matches():
#             return False
#         proj = self._item_providing(IProject)
#         mstool = getToolByName(proj, 'portal_membership')
#         if not mstool.isAnonymousUser():
#             mem = mstool.getAuthenticatedMember()
#             team = proj.getTeams()[0]
#             filter_states = tuple(team.getActiveStates()) + ('pending',)
#             if mem.getId() in team.getMemberIdsByStates(filter_states):
#                 return self.no_render()
#         return True

#     def is_selected(self):
#         return True

#     def set_css_class(self):
#         if self.request.ACTUAL_URL == self.url:
#             self.css_class = 'oc-topnav-selected'
#         else:
#             self.css_class = 'oc-topnav-join'

# # Search menu items
# class PeopleMenuItem(PortalContextMenuItem):
#     name = u'People'
#     folder_context = 'people'

#     def is_selected(self):
#         return IAmAPeopleFolder.providedBy(self.context)

# class ProjectsMenuItem(PortalContextMenuItem):
#     name = u'Projects'
#     folder_context = 'projects'

#     def is_selected(self):
#         return (IAddProject.providedBy(self.context)
#                 and not self.request.ACTUAL_URL.endswith('/create'))

# class StartProjectMenuItem(StartsWithMixin, BaseMenuItem):
#     name = u'Start A Project'

#     def context_matches(self):
#         return True

#     def get_url(self):
#         portal = getToolByName(self.context, 'portal_url').getPortalObject()
#         return '%s/%s' % (portal.projects.absolute_url(), 'create')

# # Featurelets need to only provide
# # name
# # supp_must_provide - installed marker interface
# # item_url - portion of url after project url
# class BaseFeatureletMenuItem(BaseProjectMenuItem):
#     """Base class to allow easy creation of featurelet menu items"""

#     supp_must_provide = Interface

#     def context_matches(self):
#         if not super(BaseFeatureletMenuItem, self).context_matches():
#             return False
#         proj = self._item_providing(IProject)
#         if not self.supp_must_provide.providedBy(proj):
#             return self.no_render()
#         return True