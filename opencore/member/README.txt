A member should implement IOpenMember::
    >>> mem = self.portal.portal_memberdata.m1
    >>> mem
    <OpenMember at /plone/portal_memberdata/m1>
    >>> from opencore.member.interfaces import IOpenMember
    >>> IOpenMember.providedBy(mem)
    True

---------------
member creation
---------------

We have a convenient way to handle the steps of initial member
creation::

    >>> from opencore.member.interfaces import ICreateMembers
    >>> ICreateMembers(self.portal)
    <opencore.member.factory.MemberFactory object at ...>
    >>> factory = ICreateMembers(self.portal)

There's secretly a validation member somewhere on the portal because
ploneish validation is rather silly and requires real content upon
which to validate::
    >>> factory._validation_member
    <OpenMember at /plone/portal_memberdata/validation_member>
    
There's also a way to fake a request, or at least the bits that the
validation methods on content care about::
    >>> from opencore.member.factory import _FakeRequest
    >>> req = _FakeRequest(dict(x=1,b=2))
    >>> req
    <opencore.member.factory._FakeRequest object at ...>
    >>> sorted(req.form.keys())
    ['b', 'x']
    >>> req['x']
    1
    >>> req.get('b')
    2
    
These are used to validate fields but we don't know that because of
the lovely validate method on the adapter::
    >>> factory.validate(dict(id='foo',
    ...                       email='greeble@example.com',
    ...                       password='testy',
    ...                       confirm_password='testy'))
    {}
    >>> errors = factory.validate(dict(id='m1', email='greexampledotcom'))
    >>> sorted(errors.keys())
    ['email', 'id', 'password']

We can also create a member without remembering how to go through a
complicated dance involving portal_factory and validation::
    >>> factory.create(dict(id='foo',
    ...                     email='greeble@example.com',
    ...                     password='testy',
    ...                     confirm_password='testy'))
    Called httplib2.Http.request...
    ...
    <OpenMember at /plone/portal_memberdata/foo>

Let's make sure the dude really exists and his fields were set::
    >>> mem = self.portal.portal_memberdata.foo
    >>> mem
    <OpenMember at /plone/portal_memberdata/foo>
    >>> (mem.getId(), mem.getEmail())
    ('foo', 'greeble@example.com')

If we try to create a member with errors, the factory fails without
grace; it expects you to validate before attempting creation::
    >>> factory.create(dict(id='m1',
    ...                     email='greexampledotcom',
    ...                     password='tesde',
    ...                     confirm_password='testy'))
    Traceback (most recent call last):
    ...
    BadRequest: The id "m1" is invalid - it is already in use.

If we try to create a member with fields that do not validate, the
factory does NOT fail, but creates the member with these bad fields.
This is bad and should be fixed, but this is the behavior of the code
that this was taken from (in opencore.nui.account.join)
    >>> factory.create(dict(id='darcy',
    ...                     email='greexampledotcom',
    ...                     password='tesde',
    ...                     confirm_password='testy'))
    Called httplib2.Http.request...
    ...
    <OpenMember at /plone/portal_memberdata/darcy>

    >>> mem = self.portal.portal_memberdata.darcy
    >>> mem
    <OpenMember at /plone/portal_memberdata/darcy>
    >>> (mem.getId(), mem.getEmail())
    ('darcy', 'greexampledotcom')

---------------
member workflow 
---------------

We also have a convenient way to talk about member workflow via the
IHandleMemberWorkflow adapter::
    >>> mem = self.portal.portal_memberdata.m1
    >>> from opencore.member.interfaces import IHandleMemberWorkflow
    >>> IHandleMemberWorkflow(mem)
    <opencore.member.workflow.MemberWorkflowHandler object at ...>

It lets us determine if a user's account is unconfirmed::
    >>> IHandleMemberWorkflow(mem).is_unconfirmed()
    False

We can also see the member's state directly, but this isn't part of
the interface because the whole point of this is to abstract away from
portal_workflow and hardcoded strings (so please don't do it)::
    >>> IHandleMemberWorkflow(mem)._wfstate
    'public'

We can confirm a member account that is pending confirmation::
    (if we had one but i don't feel like setting this up now)

But this method doesn't do any error checking of its own, so if we
try to confirm an account that's already confirmed we'll get an
exception from portal_workflow::
    >>> IHandleMemberWorkflow(mem).confirm()
    Traceback (most recent call last):
    ...
    WorkflowException: No workflow provides the "register_public" action.