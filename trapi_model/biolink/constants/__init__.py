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
        except ValueError as ex:
            logger.warning(str(ex))
        # Now format constant name
        formatted_name = 'BIOLINK_' + '_'.join(constant_name.strip().upper().split(' '))
        biolink_entity_name = formatted_name + '_ENTITY'
        # set the constants and entities
        try:
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
        except ValueError as ex:
            logger.warning(str(ex))

def get_biolink_entity(name):
    if not BIOLINK_DEBUG:
        return BiolinkEntity(name)
    if 'biolink:' in name:
        parsed_name = name.split(':')[-1]
        # Check if its a predicate or class based on capitalization.
        if parsed_name.lower() == parsed_name:
            # All lowercase and therefore is a predicate.
            # Convert to constants formatted name
            formatted_name = 'BIOLINK_' + '_'.join(x.upper() for x in parsed_name.split('_')) + '_ENTITY'
        else:
            # Split Camal case
            name_list = [[parsed_name[0]]]
            for c in parsed_name[1:]:
                if name_list[-1][-1].islower() and c.isupper():
                    name_list.append(list(c))
                else:
                    name_list[-1].append(c)
            name_list = [''.join(word) for word in name_list]
            formatted_name = 'BIOLINK_' + '_'.join(x.upper() for x in name_list) + '_ENTITY'
    else:
        # Just convert spaced out biolink compliant string (that has the spaces).
        formatted_name = 'BIOLINK_' + '_'.join(name.strip().upper().split(' ')) + '_ENTITY'
    # Try to return formatted name
    return getattr(
            sys.modules[__name__],
            formatted_name,
            )

