username = 'admin'
from AccessControl.SecurityManagement import newSecurityManager
user = app.acl_users.getUser(username)
user = user.__of__(app.acl_users)
newSecurityManager(app, user)
from Testing.makerequest import makerequest
app=makerequest(app)
import transaction

n = app.openplans
md = n.portal_memberdata
ms = n.portal_membership
uf = n.acl_users
at = n.portal_actions
tt = n.portal_types
wft = n.portal_workflow
cat = n.portal_catalog
tmt = n.portal_teams

import os
from App.config import getConfiguration
from zExceptions import BadRequest
from zope.component.interfaces import ComponentLookupError
sw = n.streetswiki
cfg = getConfiguration()
home = cfg.instancehome
zopeimport = os.path.join(home, 'import')

#we need to remove the frontpage-text page that gets inserted by default
#during the streetswiki folder installation
#this is necessary so that the frontpage-text page of the exported data
#gets imported in rather than skipping it and using the default
print 'removing streetswiki/frontpage-text'
sw.manage_delObjects(['frontpage-text'])
print 'successfully removed streetswiki/frontpage-text'

#keep track of the number of articles imported
n_imported = 0

for filename in os.listdir(zopeimport):
    if not filename.endswith('.zexp'):
        continue
    if filename in ('Examples.zexp', 'ZopeTutorialExamples.zexp'):
        continue
    print 'importing ' + filename
    try:
        sw.manage_importObject(filename)
        n_imported += 1
    except BadRequest:
        print '*' * 80
        print 'failed to import %s' % filename
        print '*' * 80
    except ComponentLookupError:
        print '*' * 80
        print 'component lookup error on %s' % filename
        print '*' * 80

transaction.get().note('imported %d articles' % n_imported)
print 'imported %d articles' % n_imported
transaction.commit()
