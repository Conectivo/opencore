"""
Naked Base View
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from memojito import memoizedproperty, memoize
from opencore import redirect 
from opencore.interfaces import IProject 
from topp.utils.pretty_date import prettyDate
from topp.utils.pretty_text import truncate
from zope.component import getMultiAdapter, adapts, adapter

class NakedView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getToolByName(context, 'portal_url').getPortalObject() 
        self.piv = context.unrestrictedTraverse('project_info') # TODO make more generic
        self.miv = context.unrestrictedTraverse('member_info') # TODO make more generic

    def _transclude(self):
        return self.request.get_header('X-transcluded')

    def include(self, viewname):
        if self._transclude():
            return '<a href="%s" rel="include">%s</a>' % (viewname, viewname)
        return self.context.unrestrictedTraverse(viewname).index()

    def userHasEditPrivs(self):
        """Returns true iff currently-logged-in user has edit privileges on
        this view."""
        # TODO
        return False

    def tabs(self):
        # XXX code review
        def isSelected(taburl):
            if self.context == self.context.unrestrictedTraverse(taburl):
                return 'selected'
        def isDisabled(tabRequiresEdit):
            if not (tabRequiresEdit and self.userHasEditPrivs()):
                return 'disabled'
        def getClass(taburl, tabRequiresEdit):
            return isSelected(taburl) or isDisabled(tabRequiresEdit) or ''
        names = ['View', 'Edit', 'History']
        requiresEditPrivs = [False, True, True]
        urls = [self.context._getURL() + i for i in ['', '/edit', '/versions_history_form']]
        classes = map(getClass, urls, requiresEditPrivs)
        return [dict(name=name, url=url, cssclass=cssclass) for
            name, url, cssclass in zip(names, urls, classes)]

    def _title_info(self):
        if self.piv.inProject:
            title = self.piv.fullname
            subtitle = self.context.title
        elif self.miv.inMemberArea:
            title = self.miv.membername
            subtitle = 'foo'
        else:
            title = self.context.title
            subtitle = 'bar'
        return title, subtitle

    def renderWindowTitle(self):
        title, subtitle = self._title_info()
        title, subtitle = truncate(title, max=16), truncate(subtitle, max=24)
        windowtitle = [subtitle, title, self.portal.title]
        return ' :: '.join([i for i in windowtitle if i])

    def renderTopnavTitle(self):
        title, _ = self._title_info()
        title = truncate(title, max=64)
        h1 = '<h1>%s</h1>' % title
        return '<a href="%s">%s</a>' % (self.context.absolute_url(), h1)

    def renderPageTitle(self):
        _, subtitle = self._title_info()
        subtitle = truncate(subtitle, max=256)
        return '<a href="%s">%s</a>' % (self.context.absolute_url(), subtitle)

    def nmembers(self):
        """Returns the number of members of the site."""
        # TODO
        return 1337

    def nprojects(self):
        """Returns the number of projects hosted by the site."""
        # TODO
        return 1337

    def dob(self):
        """Returns OpenPlans' "date of birth"."""
        # TODO
        return 'January 3, 1937'
