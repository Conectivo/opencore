"""
Profile View
"""
from AccessControl import allow_module
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.remember.interfaces import IReMember
from interfaces import FirstLoginEvent
from interfaces import IMemberFolder, IMemberHomePage
from interfaces import IMemberInfo, IFirstLoginEvent
from memojito import memoizedproperty, memoize
from opencore import redirect 
from opencore.interfaces import IProject 
from topp.utils.pretty_date import prettyDate
from zope.component import getMultiAdapter, adapts, adapter
from zope.event import notify
from zope.interface import implements, alsoProvides

allow_module('opencore.siteui.member')

class MemberInfoView(BrowserView):
    """A view which also provides contextual information about a member."""
    implements(IMemberInfo)

    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        self.mtool = getToolByName(context, 'portal_membership')

    @property
    def context(self):
        return self._context[0]

    def interfaceInAqChain(self, iface):
        chain = self.context.aq_chain
        for item in chain:
            if iface.providedBy(item):
                return item

    @memoizedproperty
    def member_folder(self):
        return self.interfaceInAqChain(IMemberFolder)

    @memoizedproperty
    def member_object(self):
        return self.interfaceInAqChain(IReMember)

    @memoizedproperty
    def member(self):
        """Returns the member object found by traversing the acquisition chain."""
        mf = self.member_folder
        if mf is not None:
            # XXX we shouldn't rely on the folder id matching the user id;
            #     maybe store the member id in an annotation on the folder?
            return self.mtool.getMemberById(mf.getId())
        return self.member_object

    @memoizedproperty
    def personal_folder(self):
        """Returns the folder of the authenticated member."""
        mem_id = self.mtool.getAuthenticatedMember().getId()
        return self.mtool.getHomeFolder(mem_id)

    @memoizedproperty
    def inMemberObject(self):
        return self.member_object is not None

    @memoizedproperty
    def inSelf(self):
        return self.inMemberObject and \
               self.member_object == self.mtool.getAuthenticatedMember()

    @property
    def inMemberArea(self):
        return self.member_folder is not None

    @memoizedproperty
    def inPersonalArea(self):
        return self.inMemberArea and self.member_folder == self.personal_folder


class ProfileView(BrowserView):
    implements(IMemberHomePage)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.set('disable_border', 1)
        self.info = None


    def _getPortraitURL(self, member):
        portrait = member.getProperty('portrait', None)
        return portrait and portrait.absolute_url()


    def _getWiki(self, memberfolder):
        homepage_id = memberfolder.getDefaultPage()
        if homepage_id is not None:
            homepage = memberfolder._getOb(homepage_id)
            return homepage.CookedBody()
        return ''


    def getUserInfo(self):
        """Returns a dict with user info that gets displayed on profile view"""
        if self.info is None:
            mtool = getToolByName(self.context, 'portal_membership')
            miv = getMultiAdapter((self.context, self.request), name='member_info')
            member, memberfolder = miv.member, miv.member_folder
            self.info = dict(login=member.getId(),
                             fullname=member.getFullname(),
                             membersince=prettyDate(member.created()),
                             lastlogin=prettyDate(member.getLast_login_time()),
                             location=member.getLocation(),
                             prefsurl=member.absolute_url() + '/edit',
                             portraiturl=self._getPortraitURL(member),
                             projects=member.getProjects(), # @@@ this should be indexed and then returned by a catalog call
                             wiki=self._getWiki(memberfolder),
                             editpermission=mtool.checkPermission(ModifyPortalContent, self.context),
                             isme=member == mtool.getAuthenticatedMember()
                             )
        return self.info

    def getLatestContent(self, limit_per_type=5):
        catalog = getToolByName(self.context, 'portal_catalog')
        types = ('OpenProject', 'Document')

        userinfo = self.getUserInfo()

        found = {}
        content = catalog.searchResults(Creator      = userinfo['login'],
                                        portal_type  = types,
                                        sort_on      = 'modified',
                                        sort_order   = 'reverse')

        for item in content:
            itemType = item.portal_type

            if not found.has_key(itemType):
                found[itemType] = []
            if len(found[itemType]) < limit_per_type:
                found[itemType].append(item)

        types = found.keys()
        types.sort()

        results = []

        for t in types:
            results.append({'portal_type' : t,
                            'content_items' : found[t]})

        return results
        

def notifyFirstLogin(member, request):
    notify(FirstLoginEvent(member, request))

@adapter(IFirstLoginEvent)
def create_home_directory(event):
    # TODO write tests

    member = event.member
    mtool = getToolByName(member, 'portal_membership')
    member_id = member.getId()

    folder = mtool.getHomeFolder(member_id)
    maybe_apply_member_folder_redirection(folder, event.request)
    alsoProvides(folder, IMemberFolder)


    page_id = "%s-home" % member_id
    title = "%s Home" % member_id
    folder.invokeFactory('Document', page_id, title=title)
    folder.setDefaultPage(page_id)
    
    page = getattr(folder, page_id)
    # XXX acquisition, ugh @@ huh?
    page_text = member.member_index(member_id=member_id)
    page.setText(page_text)

    # the page is the homepage
    alsoProvides(page, IMemberHomePage)

    # make profile the default view on the homepage
    page.setLayout('profile.html')


def in_project(request):
    parents = request['PARENTS']

    for parent in parents:
        # check the request for a redirected project
        if (redirect.IRedirected.providedBy(parent) and
            IProject.providedBy(parent)):
            return parent
        

def apply_member_folder_redirection(folder, request):
    if not request or not 'PARENTS' in request:
        return

    parent = get_parent_project(request) 
    if parent:
        parent_info = redirect.get_info(parent)
        folder_id = folder.getId()
        folder_path = "%s/people/%s" % (parent_info.url, folder_id)
        return redirect.activate(folder, url=folder_path)
    return redirect.activate(folder, explicit=False)



    

