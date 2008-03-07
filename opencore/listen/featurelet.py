import logging
from opencore.featurelets.interfaces import IListenContainer
from opencore.featurelets.interfaces import IListenFeatureletInstalled
from opencore.interfaces import IProject
from opencore.interfaces.event import ListenFeatureletCreatedEvent
from opencore.listen.mailinglist import OpenMailingList
from opencore.feed.interfaces import ICanFeed
from Products.CMFCore.utils import getToolByName
from Products.listen.interfaces import IListLookup
from topp.featurelets.base import BaseFeaturelet
from topp.featurelets.interfaces import IFeaturelet
from topp.featurelets.interfaces import IFeatureletSupporter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implements
from zope.event import notify


log = logging.getLogger('opencore.featurelets.listen')

class ListenFeaturelet(BaseFeaturelet):
    """
    A featurelet that installs a folder for managing listen based
    mailing lists.
    """
    implements(IFeaturelet)

    id = "listen"
    title = "Mailing lists"
    #config_view = "listen_config"
    installed_marker = IListenFeatureletInstalled
    
    _info = {'content': ({'id': 'lists', 'title': 'Mailing lists',
                          'portal_type': 'Folder'},),
             'menu_items': ({'title': u'Mailing lists',
                             'description': u'Mailing lists',
                             'action': u'lists',
                             'order': 0,
                             },
                            ),
             }

    _required_interfaces = BaseFeaturelet._required_interfaces + \
                           (IProject,)

    def deliverPackage(self, obj):
        """
        See IFeaturelet.
        """
        BaseFeaturelet.deliverPackage(self, obj)
        container = obj._getOb(self._info['content'][0]['id'])
        container.setLayout('mailing_lists')
        alsoProvides(container, IListenContainer)
        alsoProvides(container, ICanFeed)
        notify(ListenFeatureletCreatedEvent(obj))
        return self._info

    def removePackage(self, obj):
        ll = getUtility(IListLookup)
        cat = getToolByName(obj, 'portal_catalog')
        for brain in cat(portal_type=OpenMailingList.portal_type):
            ml = brain.getObject()
            ll.unregisterList(ml)
        return BaseFeaturelet.removePackage(self, obj)
