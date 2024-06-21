#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import logging
import os

import prettytable

####################################################################################################
def oab2table(data, width=None):
    """ Print our dictionary results as a PrettyTable """
    if width is None:
        if "COLUMNS" in os.environ:
            width = int(os.environ["COLUMNS"])
        else:
            width = 80

    users = prettytable.PrettyTable()
    users.field_names = ["Name", "Account", "Email", "Mobile", "Department", "Country"]
    # Distribute terminal width minus the 7 vertical borders and the 2 spaces per column
    users._max_width = {
        "Name": int(0.20 * (width - 7)) - 2,
        "Account": int(0.08 * (width - 7)) - 2,
        "Email": int(0.28 * (width - 7)) - 2,
        "Mobile": int(0.16 * (width - 7)) - 2,
        "Department": int(0.20 * (width - 7)) - 2,
        "Country": int(0.08 * (width - 7)) - 2,
    }
    users.align = "l"
    users.set_style(prettytable.SINGLE_BORDER)
    users.sortby = "Name"

    lists = prettytable.PrettyTable()
    lists.field_names = ["Name", "Account", "Email", "Members (int+ext)"]
    # Distribute terminal width minus the 5 vertical borders and the 2 spaces per column
    lists._max_width = {
        "Name": int(0.24 * (width - 5)) - 2,
        "Account": int(0.24 * (width - 5)) - 2,
        "Email": int(0.4 * (width - 5)) - 2,
        "Members (int+ext)": int(0.12 * (width - 5)) - 2,
    }
    lists.align = "l"
    lists.set_style(prettytable.SINGLE_BORDER)
    lists.sortby = "Name"

    count_users = 0
    count_lists = 0
    count_lists_without_members = 0
    count_unknown = 0

    for entry in data["address_book"]:
        record = entry["record"]

        match record["PidTagObjectType"]:
            case 6: # User
                count_users += 1
                display_name = ""
                if "PidTagDisplayName" in record:
                    display_name = record["PidTagDisplayName"]
                account = ""
                if "PidTagAddressBookDisplayNamePrintable" in record:
                    account = record["PidTagAddressBookDisplayNamePrintable"]
                elif "PidTagAccount" in record:
                    account = record["PidTagAccount"]
                email = ""
                if "PidTagSmtpAddress" in record:
                    email = record["PidTagSmtpAddress"]
                mobile = ""
                if "PidTagMobileTelephoneNumber" in record:
                    mobile = record["PidTagMobileTelephoneNumber"]
                department_name = ""
                if "PidTagDepartmentName" in record:
                    department_name = record["PidTagDepartmentName"]
                country = ""
                if "PidTagCountry" in record:
                    country = record["PidTagCountry"]

                users.add_row([display_name, account, email, mobile, department_name, country])

            case 8: # List
                count_lists += 1
                display_name = ""
                if "PidTagDisplayName" in record:
                    display_name = record["PidTagDisplayName"]
                account = ""
                if "PidTagAddressBookDisplayNamePrintable" in record:
                    account = record["PidTagAddressBookDisplayNamePrintable"]
                elif "PidTagAccount" in record:
                    account = record["PidTagAccount"]
                email = ""
                if "PidTagSmtpAddress" in record:
                    email = record["PidTagSmtpAddress"]
                members = ""
                count = 0
                if "PidTagAddressBookDistributionListMemberCount" in record:
                    count += record["PidTagAddressBookDistributionListMemberCount"]
                    members = str(record["PidTagAddressBookDistributionListMemberCount"])
                else:
                    members = "0"
                if "PidTagAddressBookDistributionListExternalMemberCount" in record:
                    count += record["PidTagAddressBookDistributionListExternalMemberCount"]
                    members += " + " + \
                        str(record["PidTagAddressBookDistributionListExternalMemberCount"])
                else:
                    members = " + 0"
                if count:
                    members = f"{str(count)} ({members})"
                else:
                    members = "0"
                    count_lists_without_members += 1

                lists.add_row([display_name, account, email, members])

            case _: # Unknown
                count_unknown += 1

    logging.info("Users count = %d", count_users)
    logging.info("Lists count = %d", count_lists)
    logging.info("Empty lists count = %d", count_lists_without_members)
    logging.info("Unknown count = %d", count_unknown)

    return users, lists
