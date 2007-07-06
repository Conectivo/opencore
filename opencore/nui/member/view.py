from datetime import datetime

from zope import event
from zope.component import getUtility

from zExceptions import BadRequest
from zExceptions import Redirect
from Missing import MV

from plone.memoize.view import memoize as req_memoize

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from topp.utils.pretty_date import prettyDate

from opencore.nui.base import BaseView, button
from opencore.nui.formhandler import OctopoLite, action
from opencore.interfaces.catalog import ILastWorkflowActor
from opencore.nui.member.interfaces import ITransientMessage
        
class ProfileView(BaseView):

    field_snippet = ZopeTwoPageTemplateFile('field_snippet.pt')

    def activity(self, max=5):
        """Returns a list of dicts describing each of the `max` most recently
        modified wiki pages for the viewed user."""
        query = dict(Creator=self.viewedmember().getId(),
                     portal_type='Document',
                     sort_on='modified',
                     sort_order='reverse',
                     limit=max)
        brains = self.catalog.searchResults(**query)

        def dictify(brain):
            return {'title': brain.Title,
                    'url':   brain.getURL(),
                    'date':  prettyDate(brain.getRawCreation_date())}

        return [dictify(brain) for brain in brains]

    def viewingself(self):
        return self.viewedmember() == self.loggedinmember

    def mangled_portrait_url(self):
        """When a member changes her portrait, her portrait_url remains the same.
        This method appends a timestamp to portrait_url to trick the browser into
        fetching the new image instead of using the cached one which could be --
        and always will be in the ajaxy-change-portrait case -- out of date.
        P.S. This is an ugly hack."""
        portrait_url = self.viewed_member_info.get('portrait_url')
        if portrait_url == self.defaultPortraitURL:
            return portrait_url
        timestamp = datetime.now().isoformat()
        return '%s?%s' % (portrait_url, timestamp)


class ProfileEditView(ProfileView, OctopoLite):

    portrait_snippet = ZopeTwoPageTemplateFile('portrait-snippet.pt')
    template = ZopeTwoPageTemplateFile('profile-edit.pt')

    @action("uploadAndUpdate")
    def change_portrait(self, target=None, fields=None):
        member = self.viewedmember()
        portrait = self.request.form.get("portrait")
        member.setPortrait(portrait)
        member.reindexObject('portrait')
        return {
            'oc-profile-avatar' : {
                'html': self.portrait_snippet(),
                'action': 'replace',
                'effects': 'highlight'
                }
            }

    @action("remove")
    def remove_portrait(self, target=None, fields=None):
        member = self.viewedmember()
        member.setPortrait("DELETE_IMAGE")  # AT API nonsense
        member.reindexObject('portrait')
        return {
            'oc-profile-avatar' : {
                'html': self.portrait_snippet(),
                'action': 'replace',
                'effects': 'highlight'
                }
            }

    @action("update")
    def handle_form(self, target=None, fields=None):
        member = self.viewedmember()
      
        # TODO resize portrait if necessary
        # TODO XXX this is dumb -- zope will do this for us.
        for field, value in self.request.form.items():
            mutator = 'set%s' % field.capitalize()
            mutator = getattr(member, mutator, None)
            if mutator is not None:
                mutator(value)
            self.user_updated()
    
        member.reindexObject()
        self.template = None
        return self.redirect('profile')
        
    def user_updated(self): # TODO
        """callback to tell taggerstore a user updated (possibly) taggifiable
        fields. something like a POST to /taggerstore/."""
        pass


class MemberPreferences(BaseView, OctopoLite):

    template = ZopeTwoPageTemplateFile('preferences.pt')
    project_row = ZopeTwoPageTemplateFile('preferences_project_row.pt')

    active_states = ['public', 'private']
    msg_category = 'membership'

    @property
    @req_memoize
    def _mship_brains(self, **extra):
        user_id = self.context.getId()
        query = dict(portal_type='OpenMembership',
                     getId=user_id,
                     )
        if extra:
            query.update(extra)
        mship_brains = self.catalogtool(**query)
        return mship_brains

    def _project_metadata_for(self, project_id):
        portal = self.portal
        portal_path = '/'.join(portal.getPhysicalPath())
        projects_folder = 'projects'
        path = [portal_path, projects_folder, project_id]
        path = '/'.join(path)

        cat = self.catalogtool
        project_info = cat.getMetadataForUID(path)
        return project_info

    def _project_id_from(self, brain):
        path = brain.getPath()
        elts = path.split('/')
        project_id = elts[-2]
        return project_id

    @req_memoize
    def _create_project_dict(self, brain):
        project_id = self._project_id_from(brain)
        project_info = self._project_metadata_for(project_id)
        proj_title = project_info['Title']
        proj_id = project_info['getId']

        made_active_date = brain.made_active_date
        if made_active_date == MV:
            mship_activated_on = 'unknown'
        else:
            mship_activated_on = self.pretty_date(brain.made_active_date)

        review_state = brain.review_state

        is_pending = review_state == 'pending'

        # pending members should also be listed as public
        # we probably could get it from the history somewhere, but for now
        # let's just assume public until someone says otherwise
        listed = is_pending or review_state == 'public'

        role = brain.highestTeamRole

        return dict(title=proj_title,
                    proj_id=proj_id,
                    since=mship_activated_on,
                    listed=listed,
                    role=role,
                    is_pending=is_pending,
                    )

    def _projects_satisfying(self, pred):
        brains = filter(pred, self._mship_brains)
        return map(self._create_project_dict, brains)

    @property
    @req_memoize
    def projects_for_user(self):
        """this should include all active mships as well as member requests"""
        def is_user_project(brain):
            if brain.review_state == 'pending':
                return brain.lastWorkflowActor == self.context.getId()
            return brain.review_state in self.active_states
        return self._projects_satisfying(is_user_project)

    @property
    @req_memoize
    def invitations(self):
        """ return mship brains for pending project invitations """
        def is_invitation(brain):
            return brain.review_state == 'pending' and \
                   brain.lastWorkflowActor != self.context.getId()
        return self._projects_satisfying(is_invitation)

    @property
    @req_memoize
    def member_requests(self):
        """ return all proj_ids for pending member requests """
        def is_member_request(brain):
            return brain.review_state == 'pending' and \
                   brain.lastWorkflowActor == self.context.getId()
        return self._projects_satisfying(is_member_request)

    def _membership_for_proj(self, proj_id):
        tmtool = self.get_tool('portal_teams')
        team = tmtool.getTeamById(proj_id)
        mem = self.context
        mem_id = mem.getId()
        mship = team._getMembershipByMemberId(mem_id)
        return mship

    def leave_project(self, proj_id):
        """ remove membership by marking the membership object as inactive """
        if not self._can_leave(proj_id): return

        mship = self._membership_for_proj(proj_id)
        wft = self.get_tool('portal_workflow')
        wft.doActionFor(mship, 'deactivate')

    def change_visibility(self, proj_id, to=None):
        """
        change whether project members appear in listings
        
        if to is None: toggles project member visibility
        if to is one of 'public', 'private': set visibility to that

        return True iff visibility changed
        """
        mship = self._membership_for_proj(proj_id)
        wft = self.get_tool('portal_workflow')
        cur_state = wft.getInfoFor(mship, 'review_state')
        if to == None:
            if cur_state == 'public':
                wft.doActionFor(mship, 'make_private')
            else:
                wft.doActionFor(mship, 'make_public')
            return True
        elif to == cur_state or to not in ('public', 'private'):
            return False
        else:
            wft.doActionFor(mship, 'make_%s' % to)
            return True

    @action('change-listing')
    def change_visilibity_handler(self, targets, fields=None):
        ret = {}
        for proj_id, field in zip(targets, fields):
            new_visibility = field['listing']
            if self.change_visibility(proj_id, new_visibility):
                ### XXX TODO how do i get projinfo for real?
                projinfo = [p for p in self.projects_for_user if p['proj_id'] == proj_id][0]
                
                ret[proj_id] = {'html': self.project_row(proj_id=proj_id,
                                                         projinfo=projinfo),
                                'action': 'replace',
                                'effects': 'highlight'}
        return ret
        
    def _can_leave(self, proj_id):
        mship = self._membership_for_proj(proj_id)
        last_actor = ILastWorkflowActor(mship).getValue()
        wft = self.get_tool('portal_workflow')
        mem_id = self.context.getId()

        review_state = wft.getInfoFor(mship, 'review_state')
        return review_state in self.active_states or \
               (review_state == 'pending' and last_actor == mem_id)

    @action('leave')
    def leave_handler(self, targets, fields=None):
        json_ret = {}
        for proj_id in targets:
            self.leave_project(proj_id)
            json_ret[proj_id] = dict(action='delete')
        return json_ret

    @property
    @req_memoize
    def infomsgs(self):
        """info messages re project admission/rejection
        
           tuples are returned in the form of (idx, msg)
           so that they can be popped by the user"""
        tm = getUtility(ITransientMessage)
        mem_id = self.context.getId()
        return tm.get_msgs(mem_id, self.msg_category)

    @property
    def n_updates(self):
        return len(self.infomsgs) + len(self.invitations)

    @property
    def invitation_actions(self):
        return ['Accept', 'Deny', 'Ignore']
