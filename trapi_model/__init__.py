import json
import os
import sys
from jsonschema import ValidationError
import copy
import itertools
from collections import defaultdict
import importlib

# Set debug mode if you don't want to load bmt
BIOLINK_DEBUG = False
BIOLINK_VERSION = 'latest'

def set_biolink_version(biolink_version):
    global BIOLINK_VERSION
    if biolink_version == BIOLINK_VERSION:
        return
    # Import available biolink schemas
    from trapi_model.data import biolink_schemas
    # Get schema directory
    bmt_schema_dir = os.path.abspath(os.path.dirname(biolink_schemas.__file__))
    available_versions = []
    found_version = False
    for schema in os.listdir(bmt_schema_dir):
        # Parse schema filename
        parse_base = os.path.splitext(os.path.basename(schema))[0]
        if 'biolink' not in parse_base:
            continue
        version = parse_base.split('-')[-1]
        if version == biolink_version:
            BIOLINK_VERSION = biolink_version
            import trapi_model.biolink
            trapi_model.biolink.set_toolkit(BIOLINK_VERSION)
            found_version = True
            break
            #importlib.reload(trapi_model.biolink)
        available_versions.append(version)
    if not found_version:
        raise ValueError(
                'Unknown Biolink Version: {}. Supported versions include: {}'.format(
                    biolink_version,
                    available_versions,
                    )
                )

def set_biolink_debug_mode(option=False):
    global BIOLINK_DEBUG
    BIOLINK_DEBUG = option
