#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import openpyxl

####################################################################################################
def oab2excel(data, filename):
    """ Output our dictionary results to a file in Excel XLSX format """
    users = []
    lists = []
    column_width = {}
    for i in range(20):
        column_width[f"users-{chr(ord('A')+i)}"] = 0
    for i in range(7):
        column_width[f"lists-{chr(ord('A')+i)}"] = 0

    for entry in data["address_book"]:
        record = entry["record"]

        match record["PidTagObjectType"]:
            case 6: # User
                display_name = ""
                if "PidTagDisplayName" in record:
                    display_name = record["PidTagDisplayName"]
                    if len(display_name) > column_width["users-A"]:
                        column_width["users-A"] = len(display_name)
                title = ""
                if "PidTagTitle" in record:
                    title = record["PidTagTitle"]
                    if len(title) > column_width["users-B"]:
                        column_width["users-B"] = len(title)
                surname = ""
                if "PidTagSurname" in record:
                    surname = record["PidTagSurname"]
                    if len(surname) > column_width["users-C"]:
                        column_width["users-C"] = len(surname)
                given_name = ""
                if "PidTagGivenName" in record:
                    given_name = record["PidTagGivenName"]
                    if len(given_name) > column_width["users-D"]:
                        column_width["users-D"] = len(given_name)
                initials = ""
                if "PidTagInitials" in record:
                    initials = record["PidTagInitials"]
                    if len(initials) > column_width["users-E"]:
                        column_width["users-E"] = len(initials)
                company_name = ""
                if "PidTagCompanyName" in record:
                    company_name = record["PidTagCompanyName"]
                    if len(company_name) > column_width["users-F"]:
                        column_width["users-F"] = len(company_name)

                account = ""
                if "PidTagAddressBookDisplayNamePrintable" in record:
                    account = record["PidTagAddressBookDisplayNamePrintable"]
                    if len(account) > column_width["users-G"]:
                        column_width["users-G"] = len(account)
                elif "PidTagAccount" in record:
                    account = record["PidTagAccount"]
                    if len(account) > column_width["users-G"]:
                        column_width["users-G"] = len(account)
                address = ""
                if "PidTagSmtpAddress" in record:
                    address = record["PidTagSmtpAddress"]
                    if len(address) > column_width["users-H"]:
                        column_width["users-H"] = len(address)
                mobile = ""
                if "PidTagMobileTelephoneNumber" in record:
                    mobile = record["PidTagMobileTelephoneNumber"]
                    if len(mobile) > column_width["users-I"]:
                        column_width["users-I"] = len(mobile)
                business_phone = ""
                if "PidTagBusinessTelephoneNumber" in record:
                    business_phone = record["PidTagBusinessTelephoneNumber"]
                if "PidTagBusiness2TelephoneNumbers" in record:
                    for number in record["PidTagBusiness2TelephoneNumbers"]:
                        business_phone += ',' + number.replace('"', "'")
                if len(business_phone) > column_width["users-J"]:
                    column_width["users-J"] = len(business_phone)
                pager = ""
                if "PidTagPagerTelephoneNumber" in record:
                    pager = record["PidTagPagerTelephoneNumber"]
                    if len(pager) > column_width["users-K"]:
                        column_width["users-K"] = len(pager)
                fax = ""
                if "PidTagPrimaryFaxNumber" in record:
                    fax = record["PidTagPrimaryFaxNumber"]
                    if len(fax) > column_width["users-L"]:
                        column_width["users-L"] = len(fax)
                home_phone = ""
                if "PidTagHomeTelephoneNumber" in record:
                    home_phone = record["PidTagHomeTelephoneNumber"]
                if "PidTagHome2TelephoneNumbers" in record:
                    for number in record["PidTagHome2TelephoneNumbers"]:
                        home_phone += ',' + number.replace('"', "'")
                if len(home_phone) > column_width["users-M"]:
                    column_width["users-M"] = len(home_phone)

                department_name = ""
                if "PidTagDepartmentName" in record:
                    department_name = record["PidTagDepartmentName"]
                    if len(department_name) > column_width["users-N"]:
                        column_width["users-N"] = len(department_name)
                office_location = ""
                if "PidTagOfficeLocation" in record:
                    office_location = record["PidTagOfficeLocation"]
                    if len(office_location) > column_width["users-O"]:
                        column_width["users-O"] = len(office_location)
                street_address = ""
                if "PidTagStreetAddress" in record:
                    street_address = record["PidTagStreetAddress"]
                    if len(street_address) > column_width["users-P"]:
                        column_width["users-P"] = len(street_address)
                postal_code = ""
                if "PidTagPostalCode" in record:
                    postal_code = record["PidTagPostalCode"]
                    if len(postal_code) > column_width["users-Q"]:
                        column_width["users-Q"] = len(postal_code)
                locality = ""
                if "PidTagLocality" in record:
                    locality = record["PidTagLocality"]
                    if len(locality) > column_width["users-R"]:
                        column_width["users-R"] = len(locality)
                state = ""
                if "PidTagStateOrProvince" in record:
                    state = record["PidTagStateOrProvince"]
                    if len(state) > column_width["users-S"]:
                        column_width["users-S"] = len(state)
                country = ""
                if "PidTagCountry" in record:
                    country = record["PidTagCountry"]
                    if len(country) > column_width["users-T"]:
                        column_width["users-T"] = len(country)

                users.append(
                    {
                        "display_name": display_name,
                        "title": title,
                        "surname": surname,
                        "given_name": given_name,
                        "initials": initials,
                        "company_name": company_name,
                        "account": account,
                        "address": address,
                        "mobile": mobile,
                        "business_phone": business_phone,
                        "pager": pager,
                        "fax": fax,
                        "home_phone": home_phone,
                        "department_name": department_name,
                        "office_location": office_location,
                        "street_address": street_address,
                        "postal_code": postal_code,
                        "locality": locality,
                        "state": state,
                        "country": country,
                    }
                )

            case 8: # List
                display_name = ""
                if "PidTagDisplayName" in record:
                    display_name = record["PidTagDisplayName"]
                    if len(display_name) > column_width["lists-A"]:
                        column_width["lists-A"] = len(display_name)
                account = ""
                if "PidTagAddressBookDisplayNamePrintable" in record:
                    account = record["PidTagAddressBookDisplayNamePrintable"]
                    if len(account) > column_width["lists-B"]:
                        column_width["lists-B"] = len(account)
                elif "PidTagAccount" in record:
                    account = record["PidTagAccount"]
                    if len(account) > column_width["lists-B"]:
                        column_width["lists-B"] = len(account)
                address = ""
                if "PidTagSmtpAddress" in record:
                    address = record["PidTagSmtpAddress"]
                    if len(address) > column_width["lists-C"]:
                        column_width["lists-C"] = len(address)
                members = 0
                internal_members = 0
                external_members = 0
                if "PidTagAddressBookDistributionListMemberCount" in record:
                    internal_members = record["PidTagAddressBookDistributionListMemberCount"]
                    if len(str(internal_members)) > column_width["lists-E"]:
                        column_width["lists-E"] = len(str(internal_members))
                if "PidTagAddressBookDistributionListExternalMemberCount" in record:
                    external_members = \
                        record["PidTagAddressBookDistributionListExternalMemberCount"]
                    if len(str(external_members)) > column_width["lists-F"]:
                        column_width["lists-F"] = len(str(external_members))
                members = internal_members + external_members
                if len(str(members)) > column_width["lists-D"]:
                    column_width["lists-D"] = len(str(members))
                comment = ""
                if "PidTagComment" in record:
                    comment = record["PidTagComment"]
                    if len(comment) > column_width["lists-G"]:
                        column_width["lists-G"] = len(comment)

                lists.append(
                    {
                        "display_name": display_name,
                        "account": account,
                        "address": address,
                        "members": members,
                        "internal_members": internal_members,
                        "external_members": external_members,
                        "comment": comment,
                    }
                )

            case _: # Unknown
                pass


    workbook = openpyxl.Workbook()

    # First tab for users
    sheet = workbook.active
    sheet.title = "Users"
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    sheet.page_setup.fitToWidth = 1
    sheet["A1"] = "Name"
    sheet["B1"] = "Title"
    sheet["C1"] = "Surname"
    sheet["D1"] = "Given name"
    sheet["E1"] = "Initials"
    sheet["F1"] = "Company"
    sheet["G1"] = "Account"
    sheet["H1"] = "Email"
    sheet["I1"] = "Mobile"
    sheet["J1"] = "Business phone"
    sheet["K1"] = "Pager"
    sheet["L1"] = "Fax"
    sheet["M1"] = "Home phone"
    sheet["N1"] = "Department"
    sheet["O1"] = "Office location"
    sheet["P1"] = "Street address"
    sheet["Q1"] = "Postal code"
    sheet["R1"] = "Locality"
    sheet["S1"] = "State or province"
    sheet["T1"] = "Country"
    for i in range(20):
        sheet.column_dimensions[f"{chr(ord('A')+i)}"].width = \
            column_width[f"users-{chr(ord('A')+i)}"]
        sheet[f"{chr(ord('A')+i)}1"].font = openpyxl.styles.Font(bold=True)
    sheet.freeze_panes = "A2"

    for i, value in enumerate(users):
        sheet[f"A{i+2}"] = value["display_name"]
        sheet[f"B{i+2}"] = value["title"]
        sheet[f"C{i+2}"] = value["surname"]
        sheet[f"D{i+2}"] = value["given_name"]
        sheet[f"E{i+2}"] = value["initials"]
        sheet[f"F{i+2}"] = value["company_name"]
        sheet[f"G{i+2}"] = value["account"]
        sheet[f"H{i+2}"] = value["address"]
        sheet[f"I{i+2}"] = value["mobile"]
        sheet[f"J{i+2}"] = value["business_phone"]
        sheet[f"K{i+2}"] = value["pager"]
        sheet[f"L{i+2}"] = value["fax"]
        sheet[f"M{i+2}"] = value["home_phone"]
        sheet[f"N{i+2}"] = value["department_name"]
        sheet[f"O{i+2}"] = value["office_location"]
        sheet[f"P{i+2}"] = value["street_address"]
        sheet[f"Q{i+2}"] = value["postal_code"]
        sheet[f"R{i+2}"] = value["locality"]
        sheet[f"S{i+2}"] = value["state"]
        sheet[f"T{i+2}"] = value["country"]
        for j in range(20):
            sheet[f"{chr(ord('A')+j)}{i+2}"].alignment = \
                openpyxl.styles.Alignment(vertical="top", wrapText=True)

    # Second tab for lists
    workbook.create_sheet(index=1, title="Lists")
    sheet = workbook.get_sheet_by_name("Lists")
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    sheet.page_setup.fitToWidth = 1
    sheet["A1"] = "Name"
    sheet["B1"] = "Account"
    sheet["C1"] = "Email"
    sheet["D1"] = "Members"
    sheet["E1"] = "Internal members"
    sheet["F1"] = "External members"
    sheet["G1"] = "Comment"
    for i in range(7):
        sheet.column_dimensions[f"{chr(ord('A')+i)}"].width = \
            column_width[f"lists-{chr(ord('A')+i)}"]
        sheet[f"{chr(ord('A')+i)}1"].font = openpyxl.styles.Font(bold=True)
    sheet.freeze_panes = "A2"

    for i, value in enumerate(lists):
        sheet[f"A{i+2}"] = value["display_name"]
        sheet[f"B{i+2}"] = value["account"]
        sheet[f"C{i+2}"] = value["address"]
        sheet[f"D{i+2}"] = value["members"]
        sheet[f"E{i+2}"] = value["internal_members"]
        sheet[f"F{i+2}"] = value["external_members"]
        sheet[f"G{i+2}"] = value["comment"]
        for j in range(7):
            sheet[f"{chr(ord('A')+j)}{i+2}"].alignment = \
                openpyxl.styles.Alignment(vertical="top", wrapText=True)

    workbook.save(filename)
