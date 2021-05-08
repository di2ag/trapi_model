DEBUG = False

import json
import os

from trapi_model.data import trapi_schemas
from trapi_model.data import biolink_schemas
from trapi_model.exceptions import UnsupportedBiolinkVersion, UnknownBiolinkEntity

# Prelink Biolink Model Toolkits
if not DEBUG:
    from bmt import Toolkit
    TOOLKITS = {'latest': Toolkit()}
'''
TOOLKITS = {}
BMT_SCHEMA_DIR = os.path.abspath(os.path.dirname(biolink_schemas.__file__))
for schema in os.listdir(BMT_SCHEMA_DIR):
    # Parse schema filename
    parse_base = os.path.splitext(os.path.basename(schema))[0]
    if 'biolink' not in parse_base:
        continue
    version = parse_base.split('-')[-1]
    TOOLKITS[version] = Toolkit(os.path.join(BMT_SCHEMA_DIR, schema))
'''

class BiolinkEntity:
    def __init__(self, name, biolink_version=None, is_slot=False):
        self.passed_name = name
        self.biolink_version = biolink_version
        self.is_slot = is_slot
        if not DEBUG:
            self.bmt = self.get_toolkit(biolink_version)
            self.element = self.bmt.get_element(name)
            if self.element is None:
                print("NO such thing as {}".format(name))
                raise UnknownBiolinkEntity(name)

    def get_curie(self, is_slot=False):
        if DEBUG:
            if 'biolink:' in self.passed_name:
                return self.passed_name
            else:
                if is_slot or self.is_slot:
                    return 'biolink:' + self.passed_name.replace(' ', '_')
                return 'biolink:' + ''.join(x for x in self.passed_name.title() if not x.isspace())
        try:
            _curie = self.element.class_uri
        except AttributeError:
            _curie = self.element.slot_uri
        return _curie

    def get_toolkit(self, biolink_version):
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


class TrapiBaseClass:
    def __init__(self, trapi_version, biolink_version):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version

    def json(self, filename=None):
        if filename is None:
            return json.dumps(self.to_dict())
        else:
            with open(filename, 'w') as json_file:
                json.dump(self.to_dict(), json_file)

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)
