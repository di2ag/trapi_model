DEBUG = False

import json
import os

from trapi_model.exceptions import UnsupportedBiolinkVersion, UnknownBiolinkEntity


class TrapiBaseClass:
    def __init__(self, trapi_version, biolink_version):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version

    def json(self, filename=None):
        if filename is None:
            return json.dumps(self.to_dict(), indent=2)
        else:
            with open(filename, 'w') as json_file:
                json.dump(self.to_dict(), json_file)

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)
