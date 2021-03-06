from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.site.localsite import disableLocalSiteHook
from opencore.upgrades.utils import run_import_step
from opencore.upgrades.utils import logger
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import providedBy

from opencore.upgrades.utils import default_profile_id

def import_opencore_profile(context):
    """
    Re-imports the entire opencore GenericSetup profile for this site.
    """
    setuptool = getToolByName(context, 'portal_setup')

    profile_id = default_profile_id()

    setuptool.runAllImportStepsFromProfile('profile-%s' % profile_id)

def fixup_list_lookup_utility(context):
    """
    Makes sure listen's IListLookup utility is installed at the portal
    level.
    """
    result = run_import_step(context, 'componentregistry',
                             profile_id='Products.listen:listen',
                             )
    logger.info(result)

def reindex_membrane_tool(context):
    """
    Triggers a reindex of the membrane_tool catalog.
    """
    mbtool = getToolByName(context, 'membrane_tool')
    mbtool.refreshCatalog()
    logger.info('Membrane tool reindexed')

def migrate_mlist_component_registries(context):
    """
    Upgrades all of the mailing lists' local component registries to
    the Five 1.5 format.
    """
    site = getToolByName(context, 'portal_url').getPortalObject()
    cat = getToolByName(context, 'portal_catalog')
    list_brains = cat.unrestrictedSearchResults(
        portal_type='Open Mailing List', sort_on='id')
    from AccessControl import getSecurityManager
    logger.debug("Running as %s" %  getSecurityManager().getUser())
    logger.debug("Got %d lists to migrate" % len(list_brains))

    for lbrain in list_brains:
        lst = lbrain.getObject()

        if 'utilities' in lst.objectIds():
            logger.debug(" MIGRATING %r" % lbrain.id)
        else:
            # We already migrated this one.
            logger.debug("    already migrated %r, skipping..." % lbrain.id)
            continue

        utilities = lst.utilities.objectItems()

        disableLocalSiteHook(lst)
        components_view = queryMultiAdapter((lst, lst.REQUEST),
                                            Interface, 'components.html')
        components_view.makeSite()
        setSite(lst)
        lst.manage_delObjects(['utilities'])

        site_manager = getSiteManager()
        for id, utility in utilities:
            info = id.split('-')
            if len(info) == 1:
                name = ''
            else:
                name = info[1]
            interface_name = info[0]

            for iface in providedBy(utility):
                if iface.getName() == interface_name:
                    site_manager.registerUtility(aq_base(utility),
                                                 iface, name=name)
            if interface_name == 'ISearchableArchive':
                lst._setObject('ISearchableArchive', aq_base(utility))

        logger.info('%s mailing list component registry migrated'
                    % lst.getId())

    logger.info('Mailing list local component registry migration complete')
