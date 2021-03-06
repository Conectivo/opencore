"""
====================
 Join by Invitation
====================

in response to `http://trac.openplans.org/openplans/ticket/1621`

This piece of architecture streamlines joining for users that have
received an invitation via email to join a project.  The invitation's
link points to a special view on the project, 'invite-join' along with
a unique key and the users email.  The view presents a join form with
a fixed email value and check boxes for any project w/ an invite for
the aforementioned address.


The process loop
================

Invites start in opencore.project.browser.manageteam.InviteView::

    >>> from Testing.makerequest import makerequest
    >>> self.portal = makerequest(self.portal); request = self.portal.REQUEST
    >>> inv = self.portal.projects.p1.unrestrictedTraverse("invite")
    >>> key=inv.do_nonmember_invitation_email('bob@bob.com', 'p5')

It is stored in the invite_utils in a keyed map::

    >>> invite_utils = getUtility(IEmailInvites)
    >>> type(invite_utils.getInvitesByEmailAddress('bob@bob.com'))
    <class 'topp.utils.persistence.KeyedMap'>

We'll simulate the link and get the invite-join view. Let's logout::

    >>> self.logout()

    >>> request.form['__k']=key
    >>> request.form['email']='bob@bob.com'
    >>> inv_join = self.portal.unrestrictedTraverse("invite-join")
    >>> inv_join
    <...InviteJoinView ...>

    >>> inv_join.email
    'bob@bob.com'

    >>> inv_join.invites
    {'p5': DateTime('...')}

The proj_ids property on the view returns the id of every project
which has been rendered in the template. Since we did not pass in
any project id when we traversed to the view, this should be empty::
    >>> inv_join.proj_ids
    []

But if we traverse to the view with a valid id for a project we've
been invited to, it will be reflected in the property.

We can't prove this for real, because the proj_ids property just reads
a variable passed in from the request. In the wild, this is generated
in a form in the template based on the 'project' key and is passed in
to the view when the form is submitted. So we'll just mock this up
very dumbly, in a way which mimics the actual behavior, so that even
if these doctests are bad tests they are at least decent docs.

    >>> request.form['project'] = 'p5'
    >>> request.form['invites'] = ['p5']

    >>> inv_join = self.portal.unrestrictedTraverse("invite-join")
    >>> inv_join.proj_ids
    ['p5']

    >>> pprint(inv_join.invite_map)
    [{'closed': False,
      'description': '',
      'id': 'p5',
      'logo': None,
      'title': 'Project F...nf',
      'url': 'http://nohost/plone/projects/p5'}]


Saving
======

First, 'create_member' checks the key::

    >>> del request.form['__k']
    >>> inv_join.validate_key()
    Traceback (most recent call last):
    ...
    BadRequest: Must present proper validation

    >>> request.form['__k'] = 'monkeys'
    >>> inv_join.validate_key()
    Traceback (most recent call last):
    ...
    ValueError: Bad confirmation key

    >>> request.form['__k']=str(key)
    >>> inv_join.validate_key()
    True

After making sure our key is valid, the view runs the JoinInv_Join's
create_member as confirmed::

    >>> request.form.update(dict(password='p@ssw0rd',
    ...                     confirm_password='p@ssw0rd',
    ...                     id='bob',
    ...                     invites=['p5']))

    >>> member = inv_join._create_member(confirmed=True)

    >>> member
    <OpenMember at /plone/portal_memberdata/bob>

    >>> member.getEmail()
    'bob@bob.com'

    >>> member.getId()
    'bob'

    >>> inv_join.confirm(member)
    True
    
    >>> inv_join.login(member.getId())

bob should be logged in::

    >>> from AccessControl import getSecurityManager
    >>> getSecurityManager().getUser()
    <MembraneUser 'bob'>

bob should have a member area::

    >>> self.portal.people['bob']
    <ATFolder at /plone/people/bob>

Finally, it processes the invites::

    >>> self.portal.portal_teams.p1['bob']
    Traceback (most recent call last):
    ...
    KeyError: 'bob'

Verify that the IJoinedProjectEvent gets fired when a member joins

    >>> from opencore.interfaces.event import IJoinedProjectEvent
    >>> from opencore.interfaces.membership import IOpenMembership
    >>> from zope.component import adapter
    >>> @adapter(IOpenMembership, IJoinedProjectEvent)
    ... def dummy_subscriber(mship, evt):
    ...     fired.append((mship, evt))

Rig up the dummy subscriber
    >>> from zope.component import provideHandler
    >>> provideHandler(dummy_subscriber)

The do_invite_joins method returns a list of projects that were joined::
    >>> inv_join.do_invite_joins(member)
    ['p5']
    >>> mbship = self.portal.portal_teams.p5['bob']
    >>> mbship
    <OpenMembership at /plone/portal_teams/p5/bob>

    >>> mbship.getTeamRoles()
    ['ProjectMember']

Check if the project joined event was fired
    >>> len(fired)
    1
    >>> mship, evt = fired[0]
    >>> mship.getId()
    'bob'
    >>> evt.__class__.__name__
    'JoinedProjectEvent'


Pending Users
=============

    >>> 

# @@ could use some edge case and error case testing in general
"""
