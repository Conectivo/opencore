from Products.Five.browser import BrowserView
from Products.OpenPlans.content.wf_policy_support import WorkflowPolicyReadAdapter
from Products.OpenPlans.content.wf_policy_support import WorkflowPolicyWriteAdapter
from Products.OpenPlans.interfaces import IReadWorkflowPolicySupport
from Products.OpenPlans.interfaces import IWriteWorkflowPolicySupport
from zope.interface import implements

class WorkflowPolicyView(BrowserView, WorkflowPolicyReadAdapter):
    """ A view that has methods for getting information about the
        default workflow policy.  This is implemented as a view rather than an
        adapter because it needs to be accessible via traversal in a template
        for AT edit forms."""

    implements(IReadWorkflowPolicySupport)

class WorkflowPolicyWriterView(BrowserView, WorkflowPolicyWriteAdapter):
    """ A view that has methods for setting the default workflow policy.  This
        is implemented as a view rather than an adapter because it needs to be 
        accessible via traversal in a template for AT edit forms."""

    implements(IWriteWorkflowPolicySupport)
