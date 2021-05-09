import logging
import json
import os

from trapi_model import BIOLINK_DEBUG, BIOLINK_VERSION
from trapi_model.data import biolink_schemas
from trapi_model.exceptions import UnsupportedBiolinkVersion, UnknownBiolinkEntity

logger = logging.getLogger(__name__)

###########
# Functions
###########

def set_toolkit(biolink_version):
    global BIOLINK_VERSION
    global TOOLKIT
    BIOLINK_VERSION = biolink_version
    from bmt import Toolkit
    if BIOLINK_VERSION == 'latest':
        logger.info('Using latest PyPy Biolink version.')
        TOOLKIT = Toolkit()
    else:
        logger.info('Loading Biolink Version {}'.format(BIOLINK_VERSION))
        BMT_SCHEMA_DIR = os.path.abspath(os.path.dirname(biolink_schemas.__file__))
        for schema in os.listdir(BMT_SCHEMA_DIR):
            # Parse schema filename
            parse_base = os.path.splitext(os.path.basename(schema))[0]
            if 'biolink' not in parse_base:
                continue
            version = parse_base.split('-')[-1]
            if version == BIOLINK_VERSION:
                TOOLKIT = Toolkit(os.path.join(BMT_SCHEMA_DIR, schema))
                break
    return

#########
# Classes
#########

class BiolinkEntity:
    def __init__(
            self,
            name,
            biolink_version=None,
            is_predicate=False,
            inverse=None,
            ancestors=None,
            ):
        if biolink_version is None:
            self.biolink_version = BIOLINK_VERSION
        elif biolink_version != BIOLINK_VERSION:
            raise ValueError('Mismatch between biolink version. You specified {} \
                    but {} is already loaded. Please reload library.'.format(
                        biolink_version,
                        BIOLINK_VERSION,
                        )
                    )
        self.passed_name = name
        self.is_predicate = is_predicate
        self.ancestors = ancestors
        self.inverse = inverse
        if not BIOLINK_DEBUG:
            self.element = TOOLKIT.get_element(name)
            if self.element is None:
                raise UnknownBiolinkEntity(name)
            self.is_predicate = TOOLKIT.is_predicate(self.element.name)
            if TOOLKIT.has_inverse(self.element.name):
                self.inverse = self.element.inverse
            self.ancestors = TOOLKIT.get_ancestors(self.element.name)

    def get_inverse(self):
        if BIOLINK_DEBUG:
            logger.warning('In debug mode, inverses might be unstable.')
            if self.inverse is not None:
                return BiolinkEntity(self.inverse, is_predicate=self.is_predicate, inverse=self.passed_name)
            else:
                return None
        if self.inverse is not None:
            return BiolinkEntity(self.inverse)
        return self.inverse

    def get_curie(self, is_predicate=False):
        if BIOLINK_DEBUG:
            if 'biolink:' in self.passed_name:
                return self.passed_name
            else:
                if is_predicate or self.is_predicate:
                    return 'biolink:' + self.passed_name.replace(' ', '_')
                return 'biolink:' + ''.join(x for x in self.passed_name.title() if not x.isspace())
        if self.is_predicate or hasattr(self.element, 'slot_uri'):
            return self.element.slot_uri
        else:
            return self.element.class_uri

    def get_ancestors(self):
        if BIOLINK_DEBUG:
            logger.warning('In debug mode, ancestors might be unstable.')
            ancestors = []
            for i, ancestor in enumerate(self.ancestors):
                if ancestor == self.passed_name:
                    continue
                ancestors.append(
                        BiolinkEntity(
                            ancestor,
                            is_predicate=self.is_predicate,
                            ancestors=ancestors[i:],
                            )
                        )
            return ancestors
        elif self.ancestors is None:
            return self.ancestors
        else:
            ancestors = [] 
            for ancestor in self.ancestors:
                if ancestor == self.element.name:
                    continue
                ancestors.append(BiolinkEntity(ancestor))
            return ancestors

    def _depreciate_get_toolkit(self, biolink_version):
        if biolink_version is None:
            return TOOLKITS['latest']
        if biolink_version not in TOOLKITS:
            raise UnsupportedBiolinkVersion(biolink_version)
        else:
            return TOOLKITS[biolink_version]
    
    def __eq__(self, other):
        if self.get_curie() == other.get_curie():
            return True
        return False

    def __hash__(self):
        return hash(self.get_curie())


##### Initialization

# Load appropriate BMT version.
if not BIOLINK_DEBUG:
    set_toolkit(BIOLINK_VERSION)
else:
    logging.warning('Running in Biolink Debug mode.')
