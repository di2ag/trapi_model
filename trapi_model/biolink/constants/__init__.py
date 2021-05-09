import os
import sys
import logging
import csv
import ast

from trapi_model import BIOLINK_DEBUG
from trapi_model.exceptions import UnknownBiolinkEntity
from trapi_model.biolink import BiolinkEntity

logger = logging.getLogger(__name__)

if BIOLINK_DEBUG:
    # Read in the debug constants file
    CONSTANTS_DIR = os.path.dirname(os.path.abspath(__file__))
    DEBUG_CONSTANTS_FILE = os.path.join(CONSTANTS_DIR, 'debug_constants.csv')
    if os.path.exists(DEBUG_CONSTANTS_FILE):
        with open(DEBUG_CONSTANTS_FILE, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                name = row[0]
                is_predicate = ast.literal_eval(row[1])
                inverse = row[2]
                if len(inverse) == 0:
                    inverse = None
                ancestors = row[3:]
                if len(ancestors) == 0:
                    ancestors = None
                biolink_entity = BiolinkEntity(
                        name,
                        is_predicate=is_predicate,
                        inverse=inverse,
                        ancestors=ancestors,
                        )
                # Now format constant name
                formatted_name = 'BIOLINK_' + '_'.join(name.strip().upper().split(' '))
                biolink_entity_name = formatted_name + '_ENTITY'
                # set the constants and entities
                setattr(
                        sys.modules[__name__],
                        formatted_name,
                        name,
                        )
                setattr(
                        sys.modules[__name__],
                        biolink_entity_name,
                        biolink_entity,
                        )
    else:
        raise FileNotFoundError('No debug biolink constants found in {}. \
                Please add a debug_constants.txt file to this directory to use this feature.')
else:
    from trapi_model.biolink import TOOLKIT
    # Will load all Biolink Entities
    for constant_name in TOOLKIT.get_all_elements():
        #print(constant_name)
        try:
            biolink_entity = BiolinkEntity(constant_name)
        except UnknownBiolinkEntity:
            logger.warning('Could not get element for {}.'.format(constant_name))
        # Now format constant name
        formatted_name = 'BIOLINK_' + '_'.join(constant_name.strip().upper().split(' '))
        biolink_entity_name = formatted_name + '_ENTITY'
        # set the constants and entities
        setattr(
                sys.modules[__name__],
                formatted_name,
                constant_name,
                )
        setattr(
                sys.modules[__name__],
                biolink_entity_name,
                biolink_entity,
                )
