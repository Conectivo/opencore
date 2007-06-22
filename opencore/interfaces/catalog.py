from zope.interface import Interface
from zope.interface.common.mapping import IReadMapping

class IIndexingGhost(Interface):

    def getValue(name, default):
        """
        Returns a value for an column or index
        that an object does not have a attribute
        or method.  
        """

class ILastWorkflowActor(Interface):

    def getValue():
        """
        Returns the 'actor' from the last workflow transition.  Used
        for membership objects to efficiently determine who requested
        the team membership.
        """

class ILastWorkflowTransitionDate(Interface):

    def getValue():
        """
        Returns the timestamp from the last workflow transition.  Used
        for membership objects to efficiently determine when the last
        workflow transition happened.
        """

class ILastModifiedAuthorId(Interface):
    """string id for last author to modify a piece of content"""

class IMetadataDictionary(IReadMapping):
    """a dictionary of all the metadata stored for an object"""
