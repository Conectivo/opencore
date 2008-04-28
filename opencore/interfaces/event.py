from zope.interface import Interface, implements
from zope.app.event.interfaces import IObjectModifiedEvent, IObjectCreatedEvent
from zope.app.event.objectevent import ObjectModifiedEvent, ObjectCreatedEvent

class IAfterProjectAddedEvent(Interface):
    """What happens after a project is added"""


class IAfterSubProjectAddedEvent(IAfterProjectAddedEvent):
    """What happens after a subproject is added"""
    

class IChangedTeamRolesEvent(IObjectModifiedEvent):
    """What happens after a membership object changed roles"""


class IJoinedProjectEvent(IObjectModifiedEvent):
    """When a user becomes an active project member"""


class ILeftProjectEvent(IObjectModifiedEvent):
    """When a user is deactivated from a project"""


class IMemberEmailChangedEvent(IObjectModifiedEvent):
    """When a user changed his email

       Necessary to add instead of just object modified event because
       the handlers for this can be expensive"""


class IListenFeatureletCreatedEvent(IObjectCreatedEvent):
    """when a listen featurelet gets installed on a project"""


class IFirstLoginEvent(Interface):
    """ Interface for FirstLoginEvent """


class JoinedProjectEvent(ObjectModifiedEvent):
    implements(IJoinedProjectEvent)


class LeftProjectEvent(ObjectModifiedEvent):
    implements(ILeftProjectEvent)


class MemberEmailChangedEvent(ObjectModifiedEvent):
    implements(IMemberEmailChangedEvent)


class AfterProjectAddedEvent(object):
    implements(IAfterProjectAddedEvent)
    def __init__(self, project, request):
        self.project = project
        self.request = request


class AfterSubProjectAddedEvent(AfterProjectAddedEvent):
    implements(IAfterSubProjectAddedEvent)

    def __init__(self, project, parent, request): 
        AfterProjectAddedEvent.__init__(self, project, request)
        self.parent = parent 


class ChangedTeamRolesEvent(ObjectModifiedEvent):
    implements(IChangedTeamRolesEvent)


class ListenFeatureletCreatedEvent(ObjectCreatedEvent):
    implements(IListenFeatureletCreatedEvent)


class FirstLoginEvent(object):
    implements(IFirstLoginEvent)
    def __init__(self, member, request):
        self.member = member
        self.request = request

