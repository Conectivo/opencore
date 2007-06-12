from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from opencore.interfaces.event import AfterProjectAddedEvent, AfterSubProjectAddedEvent
from opencore.interfaces import IAddProject, IAddSubProject 
from opencore.nui.base import BaseView, button
from opencore.nui.main import SearchView
from zExceptions import BadRequest
from zExceptions import Redirect
from zope import event
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.memoize.instance import memoizedproperty
from opencore.project.utils import get_featurelets

def octopus_form_handler(func):
    """
    A (hopefully) generic decorator to handle complex forms with
    multiple actions and multiple items which can be acted upon
    either singly or in a batch, with the call made either 
    asynchronously or synchronously with javascript disabled.

    This method expects to decorate a method which takes, in order,
      * an action to apply (a unique identifier for a method to
                            delegate to or an action to perform),
      * a list of targets (unique identifiers for items to act upon),
      * a list of fields (a dict of fieldname:values to apply to the
                          targets, in the same order as the targets)

    It expects to be returned a value to be sent, unmodified, directly
    to the client in the case of an AJAX request.

    It expects a very specific format for the request; this is 
    documented in contents.txt
    """
    def inner(self):
        # XXX todo don't rely on underscore special character
        target, action = self.request.form.get("task").split("_")

        if target == 'batch' and self.request.form.get('batch[]'):
            target = self.request.form.get("batch[]")
        if not isinstance(target, (tuple, list)):
            target = [target]

        # grab items' fields from request and fill dicts in an ordered list
        fields = []
        for item in target:
            itemdict = {}
            filterby = item + '_'
            keys = [key for key in self.request.form if key.startswith(filterby)]
            for key in keys:
                itemdict[key.replace(filterby, '')] = self.request.form.get(key)
            fields.append(itemdict)

        ret = func(self, action, target, fields)
        mode = self.request.form.get("mode")
        if mode == "async":
            return ret
        return self.redirect(self.request.environ['HTTP_REFERER'])

    return inner


class ProjectContentsView(BaseView):
    
    contents_row_snippet = ZopeTwoPageTemplateFile('item_row.pt')
    
    needed_values = {'pages':{'id':('getId',),
                              'title':('Title',),
                              'url':('getURL',
                                     'absolute_url',),
                              'obj_size':('getObjSize',),
                              'obj_date':('ModificationDate',),
                              'obj_author':('lastModifiedAuthor',),
                              },
                     'files':{'id':('getId',),
                              'title':('Title',),
                              'url':('getURL',
                                     'absolute_url',),
                              'obj_size':('getObjSize',),
                              'obj_date':('Date',),
                              'obj_author':('Creator',),
                              },
                     'lists':{'id':('getId',),
                              'title':('Title',),
                              'url':('getURL',
                                     'absolute_url',),
                              'obj_size':('getObjSize',),
                              'obj_date':('Date',),
                              'obj_author':('Creator',),
                              },
                     }

    def _make_dict_and_translate(self, obj, needed_values):
        obj_dict = {}
        for field in needed_values: # loop through fields that we need
            for obj_field in needed_values[field]: # loop through object-specific ways of getting the field
                val = getattr(obj, obj_field, None)
                if val is None: continue
                break
            if val is None:
                raise Exception("Could not fetch a %s value from the object %s among the accessors %s!" % (
                        field, obj, list(needed_values[field])))
            if callable(val): val = val()
            obj_dict[field] = val
        return obj_dict

    @memoizedproperty
    def has_mailing_lists(self):
        return self._has_featurelet('listen')

    @memoizedproperty
    def has_task_tracker(self):
        return self._has_featurelet('tasks')

    def _has_featurelet(self, flet_id):
        flets = get_featurelets(self.context)
        for flet in flets:
            if flet['name'] == flet_id:
                return True
        return False

    @memoizedproperty
    def project_path(self):
        return '/'.join(self.context.getPhysicalPath())

    @memoizedproperty
    def pages(self):
        brains = self.catalog(portal_type="Document",
                              path=self.project_path)
        needed_values = self.needed_values['pages']
        ret = []
        for brain in brains:
            d = self._make_dict_and_translate(brain, needed_values)
            if d['id'] == 'project-home':
                d['uneditable'] = True
            ret.append(d)
        return ret

    @memoizedproperty
    def lists(self):
        brains = self.catalog(portal_type="Open Mailing List",
                              path=self.project_path)
        needed_values = self.needed_values['lists']
        return [self._make_dict_and_translate(brain, needed_values) for brain in brains]


    @memoizedproperty
    def files(self):
        brains = self.catalog(portal_type=("FileAttachment","Image"),
                              path=self.project_path)
        needed_values = self.needed_values['files']
        return [self._make_dict_and_translate(brain, needed_values) for brain in brains]


    def _make_dict(self, obj, needed_values):
        obj_dict = {}
        for field in needed_values:
            val = getattr(obj, field, None)
            if val is None: continue
            if callable(val): val = val()
            obj_dict[field] = val
        return obj_dict

    @octopus_form_handler
    def modify_contents(self, action, sources, fields=None):
        item_type = self.request.form.get("item_type")

        if item_type == 'pages' and 'project-home' in sources:
            sources.remove("project-home")

        brains = self.catalog(id=sources, path=self.project_path)

        if action == 'delete':
            parents = {}
            for brain in brains:
                parent_path, brain_id = brain.getPath().rsplit('/', 1)
                parent_path = parent_path.split(self.project_path, 1)[-1].strip('/')
                parents.setdefault(parent_path, []).append(brain_id)
            for parent, child_ids in parents.items():
                if child_ids:
                    parent = self.context.restrictedTraverse(parent)
                    parent.manage_delObjects(child_ids)
            return sources

        elif action == 'update':
            snippets = {}
            objects = dict([(b.getId, b.getObject()) for b in brains])
            for old, new in zip(sources, fields):
                page = objects[old]
                page.setTitle(new['title'])
                page.reindexObject(('Title',))
                snippets[page.getId()] = self.contents_row_snippet(
                    item=self._make_dict_and_translate(page,
                                                       self.needed_values[item_type]),
                    item_type=item_type)
            
            return snippets


class ProjectPreferencesView(BaseView):
        
    @button('update')
    def handle_request(self):
        self.context.validate(REQUEST=self.request,
                              errors=self.errors, data=1, metadata=0)
        if not self.errors:
            self.context.processForm(REQUEST=self.request)
            self.redirect(self.context.absolute_url())


class ProjectAddView(BaseView):

    @button('add')
    def handle_request(self):
        putils = getToolByName(self.context, 'plone_utils')
        self.request.set('__initialize_project__', True)

        self.errors = {}
        if not self.request.get('full_name'):
            self.errors['full_name'] = 'Project requires a full name.'

        title = self.request.form.get('title')
        if not title:
            self.errors['title'] = 'Project requires a url.'
        id_ = putils.normalizeString(title)
        if self.context.has_key(id_):
            self.errors = {'title' : 'The requested url is already taken.'}

        if self.errors:
            self.addPortalStatusMessage(u'Please correct the indicated errors.')
            return 

        proj = self.context.restrictedTraverse('portal_factory/OpenProject/%s' %id_)
        proj.validate(REQUEST=self.request, errors=self.errors, data=1, metadata=0)
        if self.errors:
            transaction_note('Started creation of project: %s' %title)
            self.addPortalStatusMessage(u'Please correct the indicated errors.')
            return 

        self.context.portal_factory.doCreate(proj, id_)
        proj = self.context._getOb(id_)
        self.notify(proj)
        transaction_note('Finished creation of project: %s' %title)
        self.redirect(proj.absolute_url())

    def notify(self, project):
        event.notify(AfterProjectAddedEvent(project, self.request))



class SubProjectAddView(ProjectAddView):

    def __init__(self, context, request):
        self.parent_project = context
        fake_ctx = self.find_project_container(context, request)
        ProjectAddView.__init__(self, fake_ctx, request)

    def find_project_container(self, obj, request):
        cur = obj
        while cur is not None and not IAddProject.providedBy(cur):
            cur = aq_parent(obj)
        return cur
    
    def notify(self, project): 
        event.notify(AfterSubProjectAddedEvent(project,
                                               self.parent_project,
                                               self.request))
    
class ProjectTeamView(SearchView):

    def __init__(self, context, request):
        SearchView.__init__(self, context, request)
        project = self.context
        teams = project.getTeams()
        assert len(teams) == 1
        team = teams[0]
        self.team_path = '/'.join(team.getPhysicalPath())
        self.active_states = team.getActiveStates()
        self.sort_by = None
   
    @button('sort')
    def handle_request(self):
        self.sort_by = self.request.get('sort_by', None)

    def handle_sort_membership_date(self):
        query = dict(portal_type='OpenMembership',
                 path=self.team_path,
                 review_state=self.active_states,
                 sort_on='made_active_date',
                 sort_order='descending',
                 )
        membership_brains = self.catalog(**query)
        mem_ids = [b.getId for b in membership_brains]
        query = dict(portal_type='OpenMember',
                     getId=mem_ids,
                     )
        member_brains = self.membranetool(**query)
        lookup_dict = dict((b.getId, b) for b in member_brains)

        results = [lookup_dict.get(b.getId, None) for b in membership_brains]
        # filter out None's, which appear for admins that are not openmembers
        results = filter(None, results)
        return self._get_batch(results)

    def handle_sort_location(self):
        query = dict(portal_type='OpenMembership',
                 path=self.team_path,
                 review_state=self.active_states,
                 )
        mem_brains = self.catalog(**query)
        mem_ids = [mem_brain.getId for mem_brain in mem_brains]
        query = dict(sort_on='sortableLocation',
                     getId=mem_ids,
                     )
        results = self.membranetool(**query)
        return self._get_batch(results)

    def handle_sort_contributions(self):
        return self._get_batch([])

    def handle_sort_default(self):
        query = dict(portal_type='OpenMembership',
                     path=self.team_path,
                     review_state=self.active_states,
                     )
        mem_brains = self.catalog(**query)

        ids = [b.getId for b in mem_brains]
        query = dict(portal_type='OpenMember',
                     getId=ids,
                     sort_on='getId',
                     )
        results = self.membranetool(**query)
        return self._get_batch(results)

    @property
    @memoize
    def memberships(self):
        try:
            sort_fn = getattr(self, 'handle_sort_%s' % self.sort_by)
            return sort_fn()
        except (TypeError, AttributeError):
            return self.handle_sort_default()
            
    def projects_for_member(self, member):
        # XXX these should be brains
        projects = self._projects_for_member(member)
        # only return max 10 results
        return projects[:10]

    def more_than_ten_projects(self, member):
        projects = self._projects_for_member(member)
        return len(projects) > 10

    @memoize_contextless
    def _projects_for_member(self, member):
        return member.getProjects()

    def membership_info_for(self, member):
        mem_id = member.getId()
        project = self.context
        project_id = project.getId()
        portal_teams = getToolByName(self.context, 'portal_teams')
        team = portal_teams._getOb(project_id)
        membership = team._getOb(mem_id)

        contributions = 'XXX'
        activation = self.pretty_date(membership.made_active_date)
        modification = self.pretty_date(membership.ModificationDate())
        return dict(contributions=contributions,
                    activation=activation,
                    modification=modification,
                    )
