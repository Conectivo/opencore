from opencore.browser.base import BaseView, _
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from opencore.member.interfaces import IHandleMemberWorkflow
from opencore.utility.interfaces import IEmailSender


class AccountView(BaseView):
    """
    base class for views dealing with accounts
    distinguished by its login functionality
    """

    add_status_message = BaseView.addPortalStatusMessage
    login_snippet = ZopeTwoPageTemplateFile('login_snippet.pt')
    forgot_snippet = ZopeTwoPageTemplateFile('forgot_snippet.pt')

    @property
    def auth(self):
        acl = self.get_tool("acl_users")
        return acl.credentials_signed_cookie_auth
    
    def login(self, member_id):
        """login a user programmatically"""
        self.request.set('__ac_name', member_id)
        self.auth.login()
        # Note that login() doesn't actually seem to log us in during
        # the current request.  eg. this next line:
        self.membertool.setLoginTimes() # XXX does nothing, we're anonymous.

    def update_credentials(self, member_id):
        return self.auth.updateCredentials(self.request, self.response,
                                           member_id, None)
    
    @property
    def login_url(self):
        return "%s/login" % self.context.absolute_url()

    def logged_in_user_js(self):
        """Get info about the current member (if any), as javascript.
        (We use a callback so client knows when this script has loaded.)
        """
        info = self.member_info
        if info:
            return """
            OpenCore.prepareform({
            loggedin: true,
            id: '%(id)s',
            name: '%(fullname)s',
            profileurl: '%(url)s/profile',
            memberurl: '%(url)s',
            website: '%(website)s',
            email: '%(email)s'
            });
            """ % info
        else:
            # Not logged in.
            return """
            OpenCore.prepareform({
            loggedin: false
            });
            """

    ### methods to deal with pending members

    def is_pending(self, **query):
        matches = self.membranetool.unrestrictedSearchResults(**query)
        if len(matches) != 1:
            return
        member = matches[0].getObject()
        if IHandleMemberWorkflow(member).is_unconfirmed():
            return member

    def _confirmation_url(self, mem):
        code = mem.getUserConfirmationCode()
        return "%s/confirm-account?key=%s" % (self.siteURL, code)

    def _sendmail_to_pendinguser(self, user_name, email, url):
        """ send a mail to a pending user """
        # TODO only send mail if in the pending workflow state

        message = _(u'email_to_pending_user',
                    mapping={u'user_name':user_name,
                             u'url':url,
                             u'portal_url':self.siteURL,
                             u'portal_title':self.portal_title()})
        
        sender = IEmailSender(self.portal)

        sender.sendMail(mto=email,
                        msg=message)