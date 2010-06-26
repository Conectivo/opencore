import sys
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system
from Products.CMFCore.utils import getToolByName

try:
    portal = sys.argv[1]
except IndexError:
    portal = 'openplans'

from opencore.utils import setup

app = setup(app, site=portal)
portal = app[portal]

wf = getToolByName(portal,'portal_workflow')
cat = getToolByName(portal,'portal_catalog')
storage = getToolByName(portal,'portal_repository')
content = cat(Language='all', portal_type='Document')
total=len(content)
skipped = 0
purged = [0,0]
current=0

for obj in content:
    current+=1
    if current%10 == 0:
        print "%f%% %d more to go" % (((100.0*current)/total),total - current)
    if current%1000 == 0:
        transaction.commit()
        print "committing transaction"
    try:
        real_obj = obj.getObject()
        length = storage.getHistory(real_obj,countPurged=False)._length
        if not length or length < 2:
            print "skipping %s" % obj.getPath()
            skipped+=1
        else:
            for edition in storage.getHistory(real_obj):
                attachments = edition.object.keys()
                print "purging %s attachments from %s <version %s>" % (
                    len(attachments),
                    obj.getPath(),
                    edition.version_id)
                edition.object.manage_delObjects(list(attachments))
            # now the attachments are gone from old versions .. but they're also cleared out of portal_catalog
            # in order to make them show up on the wiki page's list of attachments, we should reindex them
            for attachment in real_obj.items():
                attachment[1].reindexObject()
    except Exception:
        import traceback
        traceback.print_exc()
        continue
            



