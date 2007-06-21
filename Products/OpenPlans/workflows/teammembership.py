#
# Generated by dumpDCWorkflow.py written by Sebastien Bigaret
# Original workflow id/title: openplans_team_membership_workflow/OpenPlans Team Membership Workflow
# Date: 2007/06/20 19:17:45.959 GMT-7
#
# WARNING: this dumps does NOT contain any scripts you might have added to
# the workflow, IT IS YOUR RESPONSABILITY TO MAKE BACKUPS FOR THESE SCRIPTS.
#
# The following scripts have been detected and should be backed up:
# - mship_activated (External Method)
#
"""
Programmatically create a workflow type.
"""
__version__ = "$Id: dumpDCWorkflow.py 31159 2006-09-28 21:40:48Z encolpe $"

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.PythonScripts.PythonScript import PythonScript
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def setup_openplans_team_membership_workflow(wf):
    """Setup the workflow
    """
    wf.setProperties(title='OpenPlans Team Membership Workflow')

    for s in ('inactive',
              'new',
              'pending',
              'private',
              'public',
              'rejected_by_admin',
              'rejected_by_owner'):
        wf.states.addState(s)
    for t in ('activate_private',
              'activate_public',
              'approve_private',
              'approve_public',
              'auto_approve_public',
              'auto_pending',
              'deactivate',
              'make_private',
              'make_public',
              'reinvite',
              'reject_by_admin',
              'reject_by_owner',
              'trigger'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for l in ('reviewer_queue',):
        wf.worklists.addWorklist(l)
    for p in ('Access contents information',
              'Modify portal content',
              'View',
              'List folder contents'):
        wf.addManagedPermission(p)

    # Initial State
    wf.states.setInitialState('new')

    # State Initialization
    sdef = wf.states['inactive']
    sdef.setProperties(title='Inactive',
                       description='',
                       transitions=('activate_private', 'activate_public', 'reinvite'))
    sdef.setPermission('Access contents information', 0,
                       ['Manager', 'ProjectAdmin', 'Reviewer'])
    sdef.setPermission('Modify portal content', 0,
                       ['Manager', 'ProjectAdmin'])
    sdef.setPermission('View', 0,
                       ['Manager', 'ProjectAdmin', 'Reviewer'])
    sdef.setPermission('List folder contents', 0,
                       ['Manager', 'ProjectAdmin'])

    sdef = wf.states['new']
    sdef.setProperties(title='',
                       description='',
                       transitions=('auto_pending', 'trigger'))
    sdef.setPermission('Access contents information', 1,
                       [])
    sdef.setPermission('Modify portal content', 1,
                       [])
    sdef.setPermission('View', 1,
                       [])
    sdef.setPermission('List folder contents', 1,
                       [])

    sdef = wf.states['pending']
    sdef.setProperties(title='Pending Approval',
                       description='',
                       transitions=('approve_private', 'approve_public', 'auto_approve_public', 'reject_by_admin', 'reject_by_owner'))
    sdef.setPermission('Access contents information', 0,
                       ['Manager', 'Owner', 'ProjectAdmin', 'Reviewer'])
    sdef.setPermission('Modify portal content', 0,
                       ['Manager', 'ProjectAdmin'])
    sdef.setPermission('View', 0,
                       ['Manager', 'Owner', 'ProjectAdmin', 'Reviewer'])
    sdef.setPermission('List folder contents', 0,
                       ['Manager', 'ProjectAdmin'])

    sdef = wf.states['private']
    sdef.setProperties(title='',
                       description='',
                       transitions=('deactivate', 'make_public'))
    sdef.setPermission('Access contents information', 1,
                       [])
    sdef.setPermission('Modify portal content', 1,
                       [])
    sdef.setPermission('View', 1,
                       [])
    sdef.setPermission('List folder contents', 1,
                       [])

    sdef = wf.states['public']
    sdef.setProperties(title='',
                       description='',
                       transitions=('deactivate', 'make_private'))
    sdef.setPermission('Access contents information', 1,
                       [])
    sdef.setPermission('Modify portal content', 1,
                       [])
    sdef.setPermission('View', 1,
                       [])
    sdef.setPermission('List folder contents', 1,
                       [])

    sdef = wf.states['rejected_by_admin']
    sdef.setProperties(title='',
                       description='',
                       transitions=('approve_private', 'approve_public', 'reinvite'))
    sdef.setPermission('Access contents information', 1,
                       [])
    sdef.setPermission('Modify portal content', 1,
                       [])
    sdef.setPermission('View', 1,
                       [])
    sdef.setPermission('List folder contents', 1,
                       [])

    sdef = wf.states['rejected_by_owner']
    sdef.setProperties(title='Reject by Owner',
                       description='',
                       transitions=('approve_private', 'approve_public', 'reinvite'))
    sdef.setPermission('Access contents information', 1,
                       [])
    sdef.setPermission('Modify portal content', 1,
                       [])
    sdef.setPermission('View', 1,
                       [])
    sdef.setPermission('List folder contents', 1,
                       [])

    # Transition Initialization
    tdef = wf.transitions['activate_private']
    tdef.setProperties(title='Activate Private',
                       description='',
                       new_state_id='private',
                       trigger_type=1,
                       script_name='',
                       after_script_name='mship_activated',
                       actbox_name='Activate',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.intended_visibility == 'private'",
                              'guard_permissions': 'TeamSpace: Manage team memberships'},
                       )

    tdef = wf.transitions['activate_public']
    tdef.setProperties(title='Activate Public',
                       description='',
                       new_state_id='public',
                       trigger_type=1,
                       script_name='',
                       after_script_name='mship_activated',
                       actbox_name='Activate',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.intended_visibility == 'public'",
                              'guard_permissions': 'TeamSpace: Manage team memberships'},
                       )

    tdef = wf.transitions['approve_private']
    tdef.setProperties(title='Approve Private',
                       description='',
                       new_state_id='private',
                       trigger_type=1,
                       script_name='',
                       after_script_name='mship_activated',
                       actbox_name='Approve',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.canApprove('private')"},
                       )

    tdef = wf.transitions['approve_public']
    tdef.setProperties(title='Approve Public',
                       description='',
                       new_state_id='public',
                       trigger_type=1,
                       script_name='',
                       after_script_name='mship_activated',
                       actbox_name='Approve',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.canApprove('public')"},
                       )

    tdef = wf.transitions['auto_approve_public']
    tdef.setProperties(title='Auto Approve Public',
                       description="Automatically approve the project creator's membership.",
                       new_state_id='public',
                       trigger_type=0,
                       script_name='',
                       after_script_name='mship_activated',
                       actbox_name='Auto Approve Public',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': 'python:container.Creator()==here.getId()'},
                       )

    tdef = wf.transitions['auto_pending']
    tdef.setProperties(title='Automatic to Pending',
                       description='',
                       new_state_id='pending',
                       trigger_type=0,
                       script_name='',
                       after_script_name='',
                       actbox_name='Automatic to Pending',
                       actbox_url='',
                       actbox_category='workflow',
                       props=None,
                       )

    tdef = wf.transitions['deactivate']
    tdef.setProperties(title='Membership is Made Inactive',
                       description='',
                       new_state_id='inactive',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Deactivate',
                       actbox_url='%(content_url)s/content_retract_form',
                       actbox_category='workflow',
                       props={'guard_permissions': 'TeamSpace: Manage team memberships'},
                       )

    tdef = wf.transitions['make_private']
    tdef.setProperties(title='Make membership private',
                       description='',
                       new_state_id='private',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Make Private',
                       actbox_url='',
                       actbox_category='workflow',
                       props=None,
                       )

    tdef = wf.transitions['make_public']
    tdef.setProperties(title='Make membership public',
                       description='',
                       new_state_id='public',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Make Public',
                       actbox_url='',
                       actbox_category='workflow',
                       props=None,
                       )

    tdef = wf.transitions['reinvite']
    tdef.setProperties(title='Reinvite an inactive user',
                       description='',
                       new_state_id='pending',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Reinvite',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_permissions': 'TeamSpace: Manage team memberships'},
                       )

    tdef = wf.transitions['reject_by_admin']
    tdef.setProperties(title='Admin Reject',
                       description='',
                       new_state_id='rejected_by_admin',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Reject',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.canReject('admin')"},
                       )

    tdef = wf.transitions['reject_by_owner']
    tdef.setProperties(title='Owner Reject',
                       description='',
                       new_state_id='rejected_by_owner',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='Reject',
                       actbox_url='',
                       actbox_category='workflow',
                       props={'guard_expr': "python:here.canReject('owner')"},
                       )

    tdef = wf.transitions['trigger']
    tdef.setProperties(title='Trigger any automatic transitions',
                       description='',
                       new_state_id='',
                       trigger_type=1,
                       script_name='',
                       after_script_name='',
                       actbox_name='',
                       actbox_url='',
                       actbox_category='workflow',
                       props=None,
                       )

    # State Variable
    wf.variables.setStateVar('review_state')

    # Variable Initialization
    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_value='',
                       default_expr='transition/getId|nothing',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed the last transition',
                       default_value='',
                       default_expr='user/getId',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_value='',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_value='',
                       default_expr='state_change/getHistory',
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_value='',
                       default_expr='state_change/getDateTime',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    # Worklist Initialization
    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending (%(count)d)',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       actbox_category='global',
                       props={'guard_permissions': 'Review portal content',
                              'var_match_review_state': 'pending'})

    # Script Initialization
    wf.scripts._setObject('mship_activated',
                          ExternalMethod('mship_activated', 'membership activated',
                                         'OpenPlans.workflow', 'mship_activated'))
    
def create_openplans_team_membership_workflow(id):
    """Create, setup and return the workflow.
    """
    ob = DCWorkflowDefinition(id)
    setup_openplans_team_membership_workflow(ob)
    return ob

addWorkflowFactory(create_openplans_team_membership_workflow,
                   id='openplans_team_membership_workflow',
                   title='OpenPlans Team Membership Workflow')
