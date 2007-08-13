"""
selective catalog metadata handling 
"""
from zope.app.event import objectevent
from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations
import zope.event
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.CMFEditions.interfaces.IArchivist import ArchivistUnregisteredError
from opencore.interfaces import IProject
from opencore.interfaces import IOpenPage
from opencore.interfaces.catalog import ILastModifiedAuthorId
from opencore.interfaces.catalog import IIndexingGhost
from Missing import MV

from Products.listen.interfaces import ISearchableMessage, ISearchableArchive, IMailMessage, IMailingList
from zope.app.event.interfaces import IObjectModifiedEvent, IObjectCreatedEvent
from zope.component import adapter
from zope.interface import alsoProvides

# where the last modified author is stored
ANNOT_KEY = 'opencore.nui.project.metadata'

### XXX todo write a test for this here -egj
@adapter(IMailMessage, IObjectModifiedEvent)
def updateThreadCount(obj, event):
    msg = ISearchableMessage(obj)
    if msg.isInitialMessage():
        # we'd like to just reindexObject on the list
        # but the new msg obj isn't really created yet
        # so we have to do a lot of nonsense instead
        ml_obj = msg
        while not IMailingList.providedBy(ml_obj):
            ml_obj = ml_obj.aq_parent
        list_path = '/'.join(ml_obj.getPhysicalPath())
        cat = getToolByName(msg, 'portal_catalog')
        md = cat.getMetadataForUID(list_path)
        md['mailing_list_threads'] += 1
        proxy = type('proxy', (object,), md)()
        cat._catalog.catalogObject(proxy, list_path, idxs=['mailing_list_threads'])

def updateContainerMetadata(obj, event):
    parent = getattr(obj, 'aq_parent', None)
    if not (parent and IProject.providedBy(parent)):
        return

    lastmodifiedauthor = ILastModifiedAuthorId(obj)

    parentuid = '/'.join(parent.getPhysicalPath())

    catalog = getToolByName(parent, 'portal_catalog')

    # make comment conditional to team security policy...
    prox = proxy(dict(lastModifiedTitle=obj.title_or_id(),
                      ModificationDate=obj.modified(),
                      lastModifiedAuthor=lastmodifiedauthor,
                      ))

    selectiveMetadataUpdate(catalog._catalog, parentuid, prox)
    catalog._catalog.catalogObject(prox, parentuid, idxs=['modified'], update_metadata=0)
    
def notifyObjectModified(obj):
    zope.event.notify(objectevent.ObjectModifiedEvent(obj))

_marker = object()

def selectiveMetadataUpdate(catalog, uid, proxy):
    index = catalog.uids.get(uid, _marker)
    if index is _marker:
        # not a cataloged item for this catalog
        return 

    old=catalog.data[index]
    old = zip(catalog.names, old)
    
    [setattr(proxy, name, value) \
     for name, value in old \
     if value is not MV \
     and not hasattr(proxy, name)]
    
    record = catalog.recordify(proxy)
    if catalog.data.get(index, 0) != record:
        catalog.data[index] = record
        catalog._p_changed = True
        catalog.data._p_changed = True

def registerMetadataGhost(name):
    def ghoster(obj, portal, **kwargs):
        try:
            ghost=IIndexingGhost(obj)
        except TypeError:
            return
        return ghost.getValue(name)
    registerIndexableAttribute(name, ghoster)
    return ghoster

@adapter(IOpenPage, IObjectModifiedEvent)
def update_last_modified_author(page, event):
    """ run when a wiki page is modified to set the last modified author """
    # find last logged in user
    mtool = getToolByName(page, 'portal_membership')
    logged_in_user = mtool.getAuthenticatedMember()
    if logged_in_user is not None:
        user_id = logged_in_user.getId()
    else:
        user_id = 'anonymous'

    # annotate page object with it
    page_annot = IAnnotations(page)
    annot = page_annot.setdefault(ANNOT_KEY, OOBTree())
    annot['lastModifiedAuthor'] = user_id

    # if part of a project, annotate the project with the user id as well
    obj = page.aq_inner
    while obj is not None:
        if IProject.providedBy(obj): break
        obj = getattr(obj, 'aq_parent', None)
    else:
        # no project found in tree
        return

    # set the project if we're in a project
    proj = obj
    proj_annot = IAnnotations(proj)
    annot = proj_annot.setdefault(ANNOT_KEY, OOBTree())
    annot['lastModifiedAuthor'] = user_id
    

def proxy(attrs):
    obj = type('metadata proxy', (object,), attrs)()
    return obj


