from opencore.configuration.utils import product_config
from pkg_resources import Requirement

OC_REQ = Requirement.parse('opencore')

# DEFAULT_ROLES should be in order from lowest to highest privilege
DEFAULT_ROLES          = ['ProjectMember', 'ProjectAdmin']
DEFAULT_ACTIVE_MSHIP_STATES=['public', 'private']
PROJECTNAME            = "OpenPlans"
# XXX HARDCODED DOMAIN
COOKIE_DOMAIN = '.openplans.org'

PROHIBITED_MEMBER_PREFIXES = ['openplans', 'topp', 'anon', 'admin',
                              'manager', 'webmaster', 'help', 'support']


