from Acquisition import aq_inner, aq_parent
from opencore.browser.base import BaseView
from opencore.browser.base import _
from opencore.browser.naming import get_view_names
from wicked.at.link import ATWickedAdd as WickedAdd
from wicked.normalize import titleToNormalizedId as normalize
from wicked.utils import getWicked
from zExceptions import Redirect
from zope.component import ComponentLookupError


class NuiBaseAdd(WickedAdd, BaseView):
    type_name = 'Document'
    extender = 'page'

    def __init__(self, context, request):
        super(NuiBaseAdd, self).__init__(context, request)
        self.errors = {}
        self.response = self.request.RESPONSE
    
    def get_container(self):
        raise NotImplementedError

    def sanitize(self, id_):
        new_id = normalize(id_)
        if new_id in self.names_for_context:
            new_id = "%s-%s" %(new_id, self.extender)
        return new_id
    
    def do_wicked(self, newcontent, title, section):
        try:
            wicked = getWicked(self.context.getField('text'), self.context)
            wicked.section=section 
            wicked.manageLink(newcontent, normalize(title))
        except ComponentLookupError:
            pass
        
    def add_content(self, title=None, section=None):
        # this is 2.5 specific and will need to be updated for new
        # wicked implementation (which is more modular)
        title = self.request.get('Title', title)
        section = self.request.get('section', section)
        assert title, 'Must have a title to create content' 
        newcontentid=self.sanitize(title)
        container = self.get_container()
        container.invokeFactory(self.type_name, id=newcontentid,
                             title=title)
        newcontent = getattr(self.context, newcontentid)
        self.do_wicked(newcontent, title, section)
        self.add_status_message(_(u'psm_page_created',
                                  u'"${pagetitle}" has been created',
                                  mapping={'pagetitle': title})
                                )
        url = newcontent.absolute_url()
        restr = "%s/edit" %url
        return self.redirect(restr)

    @property
    def names_for_context(self):
        return get_view_names(self.get_container()) 


class NuiContainerAdd(NuiBaseAdd):
    """add mechanism for a container"""

    def get_container(self):
        return aq_inner(self.context)


class NuiPageAdd(NuiBaseAdd):

    def get_container(self):
        return aq_parent(aq_inner(self.context))



    
    

