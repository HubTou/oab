#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import binascii
import io
import logging
import math
import os
import re
import struct

import rich.progress

from .properties import property_tags

####################################################################################################
def _get_file_type(file_name):
    """ Returns an OAB file type from its name """
    # The name of change files or compressed files is not known
    match file_name:
        case "ubrowse.oab":
            file_type = "browse file"
        case "uANRdex.oab":
            file_type = "ANR index file"
        case "udetails.oab":
            file_type = "details file"
        case "uPDNdex.oab":
            file_type = "PDN index file"
        case "uRDNdex.oab":
            file_type = "RDN index file"
        case "utmplts.oab":
            file_type = "display template file"
        case _:
            file_type = "unknown file"

    return file_type

####################################################################################################
def _read_OAB_HDR(file_type, file):
    """ Returns the OAB file header (OAB_HDR) """
    data = {}

    # Reading 3 little-endian unsigned int
    (data["ulVersion"], data["ulSerial"], data["ulTotRecs"]) = \
        struct.unpack('<III', file.read(4 * 3))
    match file_type:
        case "browse file":
            match data["ulVersion"]:
                case 0xa:
                    data["version"] = "uncompressed version 2 OAB browse file"
                case 0xe:
                    data["version"] = "uncompressed version 3 OAB browse file"
                case _:
                    data["version"] = "unknown file"

        case "ANR index file":
            match data["ulVersion"]:
                case 0xa:
                    data["version"] = "uncompressed version 2 ANR index file"
                case 0xe:
                    data["version"] = "uncompressed version 3 ANR index file"
                case _:
                    data["version"] = "unknown file"

        case "PDN index file":
            match data["ulVersion"]:
                case _:
                    data["version"] = "unknown file"

        case "RDN index file":
            data["oRoot"] = struct.unpack('<I', file.read(4))[0]
            match data["ulVersion"]:
                case 0xa:
                    data["version"] = "uncompressed version 2 RDN index file"
                case 0xe:
                    data["version"] = "uncompressed version 3 RDN index file"
                case _:
                    data["version"] = "unknown file"

        case "display template file":
            match data["ulVersion"]:
                case 0x7:
                    data["version"] = "uncompressed display template file"
                case _:
                    data["version"] = "unknown file"

        case "change file":
            match data["ulVersion"]:
                case 0xb:
                    data["version"] = "uncompressed version 2 changes file"
                case 0xf:
                    data["version"] = "uncompressed version 3 changes file"
                case _:
                    data["version"] = "unknown file"

        case "compressed file":
            data["ulVersionHi"] = data["ulVersion"]
            del data["ulVersion"]
            data["ulVersionLo"] = data["ulSerial"]
            del data["ulSerial"]
            data["ulBlockMax"] = data["ulTotRecs"]
            del data["ulTotRecs"]
            data["ulTargetSize"] = struct.unpack('<I', file.read(4))[0]
            if data["ulVersionHi"] == 0x2 and data["ulVersionLo"] == 0x1:
                data["version"] = "compressed version 2 or 3 OAB file"
            elif data["ulVersionHi"] == 0x3 and data["ulVersionLo"] == 0x1:
                data["version"] = "compressed version 4 OAB file"
            else:
                data["version"] = "unknown file"

        case _: # including "details file"
            match data["ulVersion"]:
                case 0x7:
                    data["version"] = "uncompressed version 2 or 3 details file"
                case 0x20:
                    data["version"] = "uncompressed version 4 full details file"
                case _:
                    data["version"] = "unknown file"

    return data

####################################################################################################
def _read_OAB_PROP_TABLE(bdata):
    """ Returns an OAB_PROP_TABLE structure contents """
    data = {}
    data["cAtts"] = struct.unpack('<I', bdata.read(4))[0]
    data["rgProps"] = []
    for _ in range(data["cAtts"]):
        ulPropId = struct.unpack('<I', bdata.read(4))[0]
        ulFlags  = struct.unpack('<I', bdata.read(4))[0]

        usPropType = ulPropId & 0x0000FFFF
        match usPropType:
            case 0x0003: property_type = "PtypInteger32"
            case 0x000B: property_type = "PtypBoolean"
            case 0x000D: property_type = "PtypObject"
            case 0x001E: property_type = "PtypString8"
            case 0x001F: property_type = "PtypString"
            case 0x0102: property_type = "PtypBinary"
            case 0x1003: property_type = "PtypMultipleInteger32"
            case 0x101E: property_type = "PtypMultipleString8"
            case 0x101F: property_type = "PtypMultipleString"
            case 0x1102: property_type = "PtypMultipleBinary"
            case _: property_type = "unknown"

        if ulPropId in property_tags:
            data["rgProps"].append((property_tags[ulPropId], property_type, ulFlags))
        else:
            data["rgProps"].append((str(ulPropId), property_type, ulFlags))

    return data

####################################################################################################
def _read_OAB_META_DATA(file):
    """ Returns the OAB metadata record (OAB_META_DATA) """
    data = {}
    data["cbSize"] = struct.unpack('<I', file.read(4))[0]

    meta_data = io.BytesIO(file.read(data["cbSize"] - 4))
    data["rgHdrAtts"] = _read_OAB_PROP_TABLE(meta_data)
    data["rgOabAtts"] = _read_OAB_PROP_TABLE(meta_data)

    return data

####################################################################################################
def _read_PtypInteger32(bdata):
    """ Returns an integer from a PTypInteger32 """
    byte_count = struct.unpack('<B', bdata.read(1))[0]
    if 0x81 <= byte_count <= 0x84:
        byte_count = struct.unpack('<I', (bdata.read(byte_count - 0x80) + b"\0\0\0")[0:4])[0]
    elif byte_count > 127:
        return -1

    return byte_count

####################################################################################################
def _read_PtypBoolean(bdata):
    """ Returns a boolean from a PTypBoolean """
    return struct.unpack('<?', bdata.read(1))[0]

####################################################################################################
def _read_PtypString(bdata):
    """ Returns a string from a PTypString or PTypString8 """
    buffer = b""
    while True:
        character = bdata.read(1)
        if character in (b"\0", b""):
            break
        buffer += character

    return buffer.decode('utf-8', errors="ignore")

####################################################################################################
def _read_PtypBinary(bdata):
    """ Returns an hexadecimal string from a PTypBinary """
    length = _read_PtypInteger32(bdata)
    binary = bdata.read(length)

    return binascii.b2a_hex(binary)

####################################################################################################
def _read_PtypMultipleString(bdata):
    """ Returns a list of strings from a PTypMultipleString or PTypMultipleString8 """
    byte_count = _read_PtypInteger32(bdata)
    strings_list = []
    for _ in range(byte_count):
        strings_list.append(_read_PtypString(bdata))

    return strings_list

####################################################################################################
def _read_PtypMultipleInteger32(bdata):
    """ Returns a list of integers from a PTypMultipleInteger32 """
    byte_count = _read_PtypInteger32(bdata)
    int_list = []
    for _ in range(byte_count):
        int_list.append(_read_PtypInteger32(bdata))

    return int_list

####################################################################################################
def _read_PtypMultipleBinary(bdata):
    """ Returns a list of hexadecimal strings from a PTypMultipleBinary """
    byte_count = _read_PtypInteger32(bdata)
    bin_list = []
    for _ in range(byte_count):
        bin_list.append(_read_PtypBinary(bdata))

    return bin_list

####################################################################################################
def _read_OAB_V4_REC(file, atts_count, attributes):
    """ Returns the OAB_V4_RECrecord """
    data = {}
    data["cbSize"] = struct.unpack('<I', file.read(4))[0]

    bdata = io.BytesIO(file.read(data["cbSize"] - 4))
    presenceBitArray = bytearray(bdata.read(int(math.ceil(atts_count / 8.0))))
    indices = [i for i in range(atts_count) if (presenceBitArray[i // 8] >> (7 - (i % 8))) & 1 == 1]

    data["record"] = {}
    for i in indices:
        attribute_name = attributes[i][0]
        attribute_type = attributes[i][1]

        match attribute_type:
            case "PtypInteger32":
                data["record"][attribute_name] = _read_PtypInteger32(bdata)
            case "PtypBoolean":
                data["record"][attribute_name] = _read_PtypBoolean(bdata)
            case "PtypObject":
                raise ValueError("Unhandled PTypObject attribute type")
            case "PtypString8":
                data["record"][attribute_name] = _read_PtypString(bdata)
            case "PtypString":
                data["record"][attribute_name] = _read_PtypString(bdata)
            case "PtypBinary":
                data["record"][attribute_name] = _read_PtypBinary(bdata)
            case "PtypMultipleInteger32":
                values = _read_PtypMultipleInteger32(bdata)
                if attribute_name == "PidTagOfflineAddressBookTruncatedProperties":
                    new_values = []
                    for value in values:
                        if value in property_tags:
                            new_values.append(property_tags[value])
                        else:
                            new_values.append(str(value))
                    values = new_values
                data["record"][attribute_name] = values
            case "PtypMultipleString8":
                data["record"][attribute_name] = _read_PtypMultipleString(bdata)
            case "PtypMultipleString":
                data["record"][attribute_name] = _read_PtypMultipleString(bdata)
            case "PtypMultipleBinary":
                data["record"][attribute_name] = _read_PtypMultipleBinary(bdata)
            case _:
                raise ValueError(f"Unhandled {attribute_type} attribute type")

    return data

####################################################################################################
def load_oab_file(path_name, progress_bar=False):
    """ Returns a dictionary with the OAB file contents """
    data = {"path_name": path_name}
    data["name"] = re.sub(f".*{os.sep}", "", path_name)

    # Determining file type
    data["type"] = _get_file_type(data["name"])
    if data["type"] == "unknown file":
        logging.warning("Unknown file type. Assuming an OAB details file")

    with open(path_name, 'rb') as file:
        data["OAB_HDR"] = _read_OAB_HDR(data["type"], file)

        if data["OAB_HDR"]["version"] == "uncompressed version 4 full details file":
            data["OAB_META_DATA"] = _read_OAB_META_DATA(file)
            data["header_record"] = _read_OAB_V4_REC(
                file,
                data["OAB_META_DATA"]["rgHdrAtts"]["cAtts"],
                data["OAB_META_DATA"]["rgHdrAtts"]["rgProps"]
            )

            if progress_bar:
                to_be_processed = rich.progress.track(
                    range(data["OAB_HDR"]["ulTotRecs"]),
                    description="Processing"
                )
            else:
                to_be_processed = range(data["OAB_HDR"]["ulTotRecs"])

            data["address_book"] = []
            for _ in to_be_processed:
                data["address_book"].append(
                    _read_OAB_V4_REC(
                        file,
                        data["OAB_META_DATA"]["rgOabAtts"]["cAtts"],
                        data["OAB_META_DATA"]["rgOabAtts"]["rgProps"]
                    )
                )
        else:
            logging.error("%s are not supported", data["OAB_HDR"]["version"])

    return data
