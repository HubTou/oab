#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

####################################################################################################
def oab2csv(data, d):
    """ Print our dictionary results in CSV format using the given delimiter to separate values """
    users = []
    users.append(
        f'"Name"{d}"Title"{d}"Surname"{d}"Given name"{d}"Initials"' +
        f'{d}"Company"{d}"Account"{d}"Email"{d}"Mobile"' +
        f'{d}"Business phone"{d}"Pager"{d}"Fax"{d}"Home phone"' +
        f'{d}"Department"{d}"Office location"{d}"Street address"' +
        f'{d}"Postal code"{d}"Locality"{d}"State or province"{d}"Country"'
    )

    lists = []
    lists.append(
        f'"Name"{d}"Account"{d}"Email"{d}"Total members"{d}"Internal members"' +
        f'{d}"External members"{d}"Comment"'
    )

    count_users = 0
    count_lists = 0
    count_lists_without_members = 0
    count_unknown = 0

    for entry in data["address_book"]:
        record = entry["record"]

        # Sanitize string values
        for key, value in record.items():
            if isinstance(value, str):
                record[key] = value.replace('"', "'").replace("\r", ". ")

        match record["PidTagObjectType"]:
            case 6: # User
                count_users += 1
                display_name = ""
                if "PidTagDisplayName" in record:
                    display_name = record["PidTagDisplayName"]
                title = ""
                if "PidTagTitle" in record:
                    title = record["PidTagTitle"]
                surname = ""
                if "PidTagSurname" in record:
                    surname = record["PidTagSurname"]
                given_name = ""
                if "PidTagGivenName" in record:
                    given_name = record["PidTagGivenName"]
                initials = ""
                if "PidTagInitials" in record:
                    initials = record["PidTagInitials"]
                company_name = ""
                if "PidTagCompanyName" in record:
                    company_name = record["PidTagCompanyName"]

                account = ""
                if "PidTagAddressBookDisplayNamePrintable" in record:
                    account = record["PidTagAddressBookDisplayNamePrintable"]
                elif "PidTagAccount" in record:
                    account = record["PidTagAccount"]
                address = ""
                if "PidTagSmtpAddress" in record:
                    address = record["PidTagSmtpAddress"]
                mobile = ""
                if "PidTagMobileTelephoneNumber" in record:
                    mobile = record["PidTagMobileTelephoneNumber"]
                business_phone = ""
                if "PidTagBusinessTelephoneNumber" in record:
                    business_phone = record["PidTagBusinessTelephoneNumber"]
                if "PidTagBusiness2TelephoneNumbers" in record:
                    for number in record["PidTagBusiness2TelephoneNumbers"]:
                        business_phone += ',' + number.replace('"', "'")
                pager = ""
                if "PidTagPagerTelephoneNumber" in record:
                    pager = record["PidTagPagerTelephoneNumber"]
                fax = ""
                if "PidTagPrimaryFaxNumber" in record:
                    fax = record["PidTagPrimaryFaxNumber"]
                home_phone = ""
                if "PidTagHomeTelephoneNumber" in record:
                    home_phone = record["PidTagHomeTelephoneNumber"]
                if "PidTagHome2TelephoneNumbers" in record:
                    for number in record["PidTagHome2TelephoneNumbers"]:
                        home_phone += ',' + number.replace('"', "'")

                department_name = ""
                if "PidTagDepartmentName" in record:
                    department_name = record["PidTagDepartmentName"]
                office_location = ""
                if "PidTagOfficeLocation" in record:
                    office_location = record["PidTagOfficeLocation"]
                street_address = ""
                if "PidTagStreetAddress" in record:
                    street_address = record["PidTagStreetAddress"]
                postal_code = ""
                if "PidTagPostalCode" in record:
                    postal_code = record["PidTagPostalCode"]
                locality = ""
                if "PidTagLocality" in record:
                    locality = record["PidTagLocality"]
                state = ""
                if "PidTagStateOrProvince" in record:
                    state = record["PidTagStateOrProvince"]
                country = ""
                if "PidTagCountry" in record:
                    country = record["PidTagCountry"]

                users.append(
                    f'"{display_name}"{d}"{title}"{d}"{surname}"{d}"{given_name}"{d}"{initials}"' +
                    f'{d}"{company_name}"{d}"{account}"{d}"{address}"{d}"{mobile}"' +
                    f'{d}"{business_phone}"{d}"{pager}"{d}"{fax}"{d}"{home_phone}"' +
                    f'{d}"{department_name}"{d}"{office_location}"{d}"{street_address}"' +
                    f'{d}"{postal_code}"{d}"{locality}"{d}"{state}"{d}"{country}"'
                )

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
                address = ""
                if "PidTagSmtpAddress" in record:
                    address = record["PidTagSmtpAddress"]
                members = 0
                internal_members = 0
                external_members = 0
                if "PidTagAddressBookDistributionListMemberCount" in record:
                    internal_members = record["PidTagAddressBookDistributionListMemberCount"]
                if "PidTagAddressBookDistributionListExternalMemberCount" in record:
                    external_members = \
                        record["PidTagAddressBookDistributionListExternalMemberCount"]
                members = internal_members + external_members
                if not members:
                    count_lists_without_members += 1
                comment = ""
                if "PidTagComment" in record:
                    comment = record["PidTagComment"]

                lists.append(
                    f'"{display_name}"{d}"{account}"{d}"{address}"{d}{members}' +
                    f'{d}{internal_members}{d}{external_members}{d}"{comment}"'
                )

            case _: # Unknown
                count_unknown += 1

    return users, lists
