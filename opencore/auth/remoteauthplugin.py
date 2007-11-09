from urllib import urlencode

from zope import event
from zope.interface import implements
from zope.component import getUtility

from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.CMFCore.utils import getToolByName

from opencore.utility.interfaces import IHTTPClient

from event import RemoteLoginSucceeded


manage_addOpenCoreRemoteAuthForm = PageTemplateFile(
        "zmi/OpenCoreRemoteAuthPluginForm.pt", globals(),
        __name__="manage_addOpenCoreRemoteAuthForm")


def manage_addOpenCoreRemoteAuth(dispatcher, id, title=None, REQUEST=None):
    """Add an OpenCore remote auth plugin to a Pluggable
    Authentication Service acl_users."""
    authplugin = RemoteOpenCoreAuth(id, title)
    dispatcher._setObject(authplugin.id, authplugin)

    if REQUEST is not None:
        query = urlencode({'manage_tabs_message':
                           'OpenCore+remote+auth+plugin+added.',
                           },
                          )
        REQUEST.RESPONSE.redirect(
                '%s/manage_workspace?%s'
                % (dispatcher.absolute_url(),
                   query)
                )


class RemoteOpenCoreAuth(BasePlugin):
    """
    Authenticates against a set of remote authentication providers.
    Fires an event upon successful authentication.  The URLs of the
    remote auth providers are retrieved from a 'remote_auth_sites'
    property (of 'lines' type) on the opencore_properties property
    sheet.
    """
    meta_type = 'OpenCore Remote Authentication'
    
    implements(IAuthenticationPlugin)

    def __init__(self, id, title=None):
        self.id = id
        self.title = title

    #
    # IAuthenticationPlugin implementation
    #
    def authenticateCredentials(self, credentials):
        """
        Iterate through the remote servers and test the credentials
        against each one in turn.
        """
        if credentials.get('opencore_auth_match'):
            # opencore.content.member.OpenMember's verifyCredentials
            # method marks the credentials object if the username was
            # indeed a match so that we know not to try remotely here.
            # we have to do this b/c PAS always invokes _every_ auth
            # plug-in during the auth check
            return

        username = credentials.get('login')
        root_uf = self.getPhysicalRoot().acl_users
        if root_uf.getUserById(username) is not None:
            # user exists at the Zope root, don't check remotely
            return

        ptool = getToolByName(self, 'portal_properties')
        ocprops = ptool._getOb('opencore_properties')
        remote_auth_sites = ocprops.getProperty('remote_auth_sites')
        if not remote_auth_sites:
            return

        password = credentials.get('password')
        query = urlencode({'__ac_password': password})
        h = getUtility(IHTTPClient)
        for siteurl in remote_auth_sites:
            if not siteurl:
                continue
            authurl = '%s/people/%s/get-hash' % (siteurl, username)
            resp, content = h.request(authurl, 'POST', query)
            resp_code = resp.get('status')
            if resp_code == '200':
                # remote auth succeeds, we're done
                event.notify(event = RemoteLoginSucceeded(self,
                                                          username,
                                                          password,
                                                          siteurl))
                # we use same value for userid and username
                return username, username

        # all auth attempts failed
        return

InitializeClass(RemoteOpenCoreAuth)
