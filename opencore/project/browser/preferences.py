"""
Preference view
"""
from DateTime import DateTime
from OFS.interfaces import IObjectWillBeRemovedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.TeamSpace.interfaces import ITeamSpaceTeamRelation
from opencore.browser import formhandler
from opencore.browser import tal
from opencore.browser.base import _, BaseView
from opencore.browser.formhandler import OctopoLite, action
from opencore.interfaces import IHomePage
from opencore.interfaces import IProject
from opencore.interfaces.adding import IAddProject
from opencore.interfaces.workflow import IReadWorkflowPolicySupport
from opencore.project.browser.base import ProjectBaseView
from opencore.tasktracker.featurelet import TaskTrackerFeaturelet
from topp.clockqueue.interfaces import IClockQueue
from topp.featurelets.interfaces import IFeatureletSupporter
from topp.featurelets.supporter import FeatureletSupporter, IFeaturelet
from topp.utils import text
from topp.utils import zutils
from zope.app.container.contained import IObjectRemovedEvent
from zope.component import adapter, adapts
from zope.component import getAdapters, queryAdapter
from zope.interface import implements
import inspect
import logging
import traceback
import zExceptions


log = logging.getLogger('opencore.project.browser.preferences')

class ProjectPreferencesView(ProjectBaseView, OctopoLite):

    template = ZopeTwoPageTemplateFile('preferences.pt')

    def mangled_logo_url(self):
        """When a project logo is changed, the logo_url remains the same.
        This method appends a timestamp to logo_url to trick the browser into
        fetching the new image instead of using the cached one which could be --
        out of date (and always will be in the ajaxy case).
        """
        logo = self.context.getLogo()
        if logo:
            timestamp = str(DateTime()).replace(' ', '_')
            return '%s?%s' % (logo.absolute_url(), timestamp)
        return self.defaultProjLogoURL

    @action("uploadAndUpdate")
    def change_logo(self, logo=None, target=None, fields=None):
        if logo is None or isinstance(logo, list):
            logo = self.request.form.get("logo")
            
        try:
            self.set_logo(logo)
        except ValueError: # @@ this hides resizing errors
            return

        self.context.reindexObject('logo')
        return {
            'oc-project-logo' : {
                'html': self.logo_html,
                'action': 'replace',
                'effects': 'highlight'
                }
            }

    def set_logo(self, logo):
        try:
            self.context.setLogo(logo)
        except ValueError: # must have tried to upload an unsupported filetype
            # is this the only kind of ValueError that could be raised?
            self.addPortalStatusMessage('Please choose an image in gif, jpeg, png, or bmp format.')
            raise

    @property
    def logo_html(self):
        macro = self.template.macros['logo']
        return tal.render(macro, tal.make_context(self))

    @action("remove")
    def remove_logo(self, target=None, fields=None):
        proj = self.context
        proj.setLogo("DELETE_IMAGE")  # blame the AT API
        proj.reindexObject('logo')
        return {
                'oc-project-logo' : {
                    'html': self.logo_html,
                    'action': 'replace',
                    'effects': 'highlight'
                    }
                }

    @formhandler.button('update')
    def handle_request(self):
        title = self.request.form.get('title')
        title = text.strip_extra_whitespace(title)
        self.request.form['title'] = title
        if not self.valid_title(title):
            self.errors['title'] = _(u'err_project_name', u'The project name must contain at least 2 characters with at least 1 letter or number.')

        if self.errors:
            self.add_status_message(_(u'psm_correct_errors_below', u'Please correct the errors indicated below.'))
            return

        allowed_params = set(['__initialize_project__', 'update', 'set_flets',
                              'title', 'description', 'logo', 'workflow_policy',
                              'featurelets', 'home-page'])
        new_form = {}
        for k in allowed_params:
            if k in self.request.form:
                new_form[k] = self.request.form[k]

        reader = IReadWorkflowPolicySupport(self.context)
        old_workflow_policy = reader.getCurrentPolicyId()

        logo = self.request.form.get('logo')
        logochanged = False
        if logo:
            try:
                self.set_logo(logo)
                logochanged = True
            except ValueError:
                pass
            del self.request.form['logo']

        #store change status of flet, security, title, description, logo
        changed = {
            _(u'psm_project_title_changed', u"The title has been changed.") : self.context.title != self.request.form.get('title', self.context.title),
            _(u'psm_project_desc_changed', u"The description has been changed.") : self.context.description != self.request.form.get('description', self.context.description),
            _(u'psm_project_logo_changed', u"The project image has been changed.") : logochanged,
            _(u'psm_security_changed', u"The security policy has been changed.") : old_workflow_policy != self.request.form['workflow_policy'],            
            }
        
        supporter = IFeatureletSupporter(self.context)
        flets = [f for n, f in getAdapters((supporter,), IFeaturelet)]

        old_featurelets = set([(f.id, f.title) for f in flets if f.installed])
            
        self.request.form = new_form
        self.context.processForm(REQUEST=self.request, metadata=1)
        featurelets = set([(f.id, f.title) for f in flets if f.installed])

        for flet in featurelets:
            if flet not in old_featurelets:
                changed[_(u'psm_featurelet_added', u'${flet} feature has been added.',
                          mapping={u'flet':flet[1].capitalize()})] = 1
        
        for flet in old_featurelets:
            if flet not in featurelets:
                changed[_(u'psm_featurelet_removed', u'${flet} feature has been removed.',
                          mapping={u'flet':flet[1].capitalize()})] = 1

        
        for field, changed in changed.items():
            if changed:
                self.add_status_message(field)
        #self.add_status_message('Your changes have been saved.')

        home_page = self.request.form.get('home-page', None)
        hpcontext = IHomePage(self.context)
        if home_page is not None:
            if hpcontext.home_page != home_page:
                hp_url = '%s/%s' % (self.context.absolute_url(), home_page)
                self.add_status_message(_(u'psm_proj_homepage_change', u'Project home page set to: <a href="${hp_url}">${homepage}</a>',
                                        mapping={u'homepage':home_page, u'hp_url':hp_url}))
                hpcontext.home_page = home_page


        self.redirect(self.context.absolute_url())

    def current_home_page(self):
        return IHomePage(self.context).home_page

    def featurelets(self):
        supporter = IFeatureletSupporter(self.context)
        all_flets = [flet for name, flet in getAdapters((supporter,), IFeaturelet)]
        installed_flets = [flet.id for flet in all_flets if flet.installed]
        flet_data = [dict(id=f.id,
                          title=f.title,
                          url=f._info['menu_items'][0]['action'],
                          checked=f.id in installed_flets,
                          )
                     for f in all_flets]
        return flet_data

    def homepages(self):
        """possible homepages for the app"""        

        flet_data = self.intrinsic_homepages() + self.featurelets()
        return flet_data


class ProjectDeletionView(BaseView):
    
    def _handle_delete(self):
        proj_folder = zutils.aq_iface(self, IAddProject)
        title = self.context.Title()
        proj_id = self.context.getId()
        proj_folder.manage_delObjects([proj_id])
        self.add_status_message("You have permanently deleted '%s' " %title)
        self.redirect("%s/create" %proj_folder.absolute_url())
        return True
    handle_delete = formhandler.button('delete')(_handle_delete)


@adapter(IProject, IObjectWillBeRemovedEvent)
def handle_flet_uninstall(project, event=None):
    supporter = IFeatureletSupporter(project)
    for flet_id in supporter.getInstalledFeatureletIds():
        supporter.removeFeaturelet(flet_id, raise_error=False)

@adapter(IProject, IObjectRemovedEvent)
def delete_team(proj, event=None):
    pt = getToolByName(proj, 'portal_teams')
    # it's a bit inelegant to rely on matching ids, but this is fine
    # as long as we have a 1:1 relation btn teams and projects
    team_id = proj.getId()
    if pt.has_key(team_id):
        pt.manage_delObjects([team_id])

@adapter(IProject, IObjectWillBeRemovedEvent)
def handle_blog_delete(project, event=None):
    pass

class ProjectFeatureletSupporter(FeatureletSupporter):
    adapts(IProject)
    implements(IFeatureletSupporter)

    def removeFeaturelet(self, featurelet, raise_error=True):
        """
        See IFeatureletSupporter.
        """
        name, featurelet=self._fetch_featurelet(featurelet)
        if self.storage.has_key(name):
            if 'raise_error' in inspect.getargspec(featurelet.removePackage)[0]:
                featurelet.removePackage(self.context, raise_error=raise_error)
            else:
                featurelet.removePackage(self.context)
            self.storage.pop(name)
                
