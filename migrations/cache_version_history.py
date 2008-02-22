from pprint import pprint 
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system
from opencore.nui.wiki import utils
import sys
import transaction as txn

newSecurityManager(None, system)

try:
    portal = sys.argv[1]
except IndexError:
    portal = 'openplans'

portal = getattr(app, portal)
pc = portal.portal_catalog
pr = portal.portal_repository
path = '/'.join(portal.getPhysicalPath() + ('projects',))
brains = pc(portal_type="Document", path=path)

print "\nattempting to migrate %s @ %s" %(len(brains), path)

def count():
    x = 0
    while True:
        x += 1
        yield x
        
counter = count()
skipcounter = count()
_ghosts = []
entries = 0

try:
    for brain in brains:
        try:
            page = brain.getObject()
        except AttributeError:
            # kill ghost
            skipcounter.next()
            _ghosts.append(brain.getPath())
            pc.uncatalog_object(brain.getPath())
            txn.commit()
            continue
        
        page._p_jar.sync()
        if getattr(page, '__HISTORY_MIGRATED__', False):
            skipcounter.next()
            continue

        result = utils.cache_history(page, pr)
        mcount = scount = 0
        
        if result:
            txn.commit()
            mcount = counter.next()
            entries += result
        elif result is False:
            scount = skipcounter.next()
        elif result == 0:
            print "no history: %s" %brain.getPath()
            
        i = mcount + scount
        if i and not i % 100:
            print "%s docs migrated" %i
            
except KeyboardInterrupt, e:
    print e

print ""
print "Total pages migrated: % 3s" %(counter.next() - 1)
print "Total entries migrated: % 1s" %(entries) 
print "Total skipped: % 10s" %(skipcounter.next() - 1)
print "Total ghosts removed: % 3s" %len(_ghosts)
if _ghosts:
    pprint(_ghosts)


