#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
Except: snippet of code from Mark@StackOverflow
"""

import base64
import json

####################################################################################################
# The following code snippet comes from:
# Author: Mark (https://stackoverflow.com/users/2606953/mark)
# Source: https://stackoverflow.com/questions/40000495/
#                                   how-to-encode-bytes-in-json-json-dumps-throwing-a-typeerror
class BytesEncoder(json.JSONEncoder):
    """ Custom class to convert binary fields to strings in JSON """
    def default(self, o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode("ascii")
        return super().default(o)

####################################################################################################
def oab2json(data, compact=False, indent=4):
    """ Convert our dictionary results to JSON """
    results = None

    if compact:
        results = json.dumps(data, cls=BytesEncoder)
    else:
        results = json.dumps(data, indent=indent, cls=BytesEncoder)

    return results
