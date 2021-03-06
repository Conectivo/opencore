"""
===================
 First Login Event
===================

When a use logins for the first time, we want to create a properly
configured user folder to hang lots of user specific fancyness
on. We'll simulate this by some hand manipulation of zope.

First, we'll get logged in at a low level::

    >>> site = self.app.plone
    >>> self.login('m1')

We hand trigger the event. Normally the login form would call this
python script object.  The result is the same as calling
'opencore.member.browser.miv.create_home_directory', but checks our
registrations::

    >>> self.app.plone.portal_membership.createMemberArea('m1')

Now we have a folder for 'm1'::

    >>> site.people.m1
    <ATFolder at /plone/people/m1>

    >>> folder = site.people.m1

It provides the proper interface::

    >>> IMemberFolder.providedBy(folder)
    True

The member homepage uses the proper layout::

    >>> folder.getLayout()
    'profile'

The member wiki page is marked with the proper interface::

    >>> defpage = getattr(folder, 'm1-home')
    >>> IMemberHomePage.providedBy(defpage)
    True
"""
