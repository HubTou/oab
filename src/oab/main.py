#!/usr/bin/env python3
""" oab - Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
Except: snippet of code from Wolph@StackOverflow
"""

import contextlib
import getopt
import logging
import os
import pprint
import sys

import libpnu

from .library import load_oab_file
from .csv_output import oab2csv
from .excel_output import oab2excel
from .json_output import oab2json
from .table_output import oab2table

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: oab - Offline Address Books decoder v1.0.0 (June 21, 2024) by Hubert Tournier $"

# Default parameters. Can be overcome by environment variables, then command line options
parameters = {
    "format": "txt",
    "progress_bar": True,
    "filename": "",
    # Parameters for CSV format
    "delimiter": ',',
    # Parameters for JSON format
    "compact": False,
    "indent": 4,
    # Parameters for PrettyTable format
    "width": None,
}

####################################################################################################
def _display_help():
    """ Display usage and help """
    #pylint: disable=C0301
    print("usage: oab [--debug] [--help|-?] [--version]", file=sys.stderr)
    print("       [--bar|-b] [--output|-o FILE]", file=sys.stderr)
    print("       [--csv|-C] [--delimiter|-d CHAR] [--excel|-E]", file=sys.stderr)
    print("       [--json|-J] [--compact|-c] [--ident|-i INT]", file=sys.stderr)
    print("       [--table|-T] [--width|-w INT]", file=sys.stderr)
    print("       [--] filename", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --bar|-b             Toggle OFF progress bar", file=sys.stderr)
    print("  --output|-o FILE     Output result into FILE (extension added by oab)", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --csv|-C             Format results as CSV", file=sys.stderr)
    print("  --delimiter|-d CHAR  Use CHAR as delimiter for CSV format", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --excel|-E           Format results as Excel tabbed file", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --json|-J            Format results as JSON", file=sys.stderr)
    print("  --compact|-c         Use compact JSON format", file=sys.stderr)
    print("  --ident|-i INT       Use INT spaces for indented JSON format", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --table|-T           Format results as tables", file=sys.stderr)
    print("  --width|-w INT       Use INT columns in table format", file=sys.stderr)
    print("  -------------------  --------------------------------------------------", file=sys.stderr)
    print("  --debug              Enable debug mode", file=sys.stderr)
    print("  --help|-?            Print usage and this help message and exit", file=sys.stderr)
    print("  --version            Print version and exit", file=sys.stderr)
    print("  --                   Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)
    #pylint: enable=C0301

####################################################################################################
def _process_command_line():
    """ Process command line options """
    #pylint: disable=C0103, W0602
    global parameters
    #pylint: enable=C0103, W0602

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "CEJTbcd:i:o:w:?"
    string_options = [
        "bar",
        "compact",
        "csv",
        "debug",
        "delimiter=",
        "excel",
        "help",
        "indent=",
        "json",
        "output=",
        "table",
        "version",
        "width=",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical("Syntax error: %s", error)
        _display_help()
        sys.exit(1)

    for option, argument in options:

        if option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("--help", "-?"):
            _display_help()
            sys.exit(0)

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(0)

        elif option in ("--bar", "-b"):
            parameters["progress_bar"] = False

        elif option in ("--compact", "-c"):
            parameters["compact"] = True

        elif option in ("--csv", "-C"):
            parameters["format"] = "csv"

        elif option in ("--delimiter", "-d"):
            parameters["delimiter"] = argument[0]

        elif option in ("--excel", "-E"):
            parameters["format"] = "excel"

        elif option in ("--indent", "-i"):
            try:
                parameters["indent"] = int(argument)
            except ValueError:
                logging.warning("Invalid argument for --indent option. Keeping default value")
            if parameters["indent"] < 0:
                logging.warning("Invalid argument for --indent option. Keeping default value")
                parameters["indent"] = 4

        elif option in ("--json", "-J"):
            parameters["format"] = "json"

        elif option in ("--output", "-o"):
            parameters["filename"] = argument

        elif option in ("--table", "-T"):
            parameters["format"] = "table"

        elif option in ("--width", "-w"):
            try:
                parameters["width"] = int(argument)
            except ValueError:
                logging.warning("Invalid argument for --width option. Keeping default value")
            if parameters["width"] < 80:
                logging.warning("Invalid argument for --width option. Keeping default value")
                parameters["width"] = None

    return remaining_arguments

####################################################################################################
# The following code is from:
# Author: Wolph https://stackoverflow.com/users/54017/wolph
# Source: https://stackoverflow.com/questions/17602878/
#                                   how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename=None):
    """ Opens files and stdout streams in the same way """
    if filename and filename != '-':
        fh = open(filename, 'w', encoding="utf-8", errors="ignore")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()

####################################################################################################
def main():
    """ The program's main entry point """
    program_name = os.path.basename(sys.argv[0])

    libpnu.initialize_debugging(program_name)
    libpnu.handle_interrupt_signals(libpnu.interrupt_handler_function)
    arguments = _process_command_line()

    if not arguments:
        _display_help()
    else:
        argument = arguments[0]
        if os.path.isfile(argument):
            data = load_oab_file(argument, progress_bar=parameters["progress_bar"])
            match parameters["format"]:
                case "csv":
                    users, lists = oab2csv(data, parameters["delimiter"])
                    filename = parameters["filename"]
                    if filename:
                        filename += ".users.csv"
                        print(f"Writing to {filename}")
                    with smart_open(filename) as file:
                        for item in users:
                            print(item, file=file)

                    filename = parameters["filename"]
                    if filename:
                        filename += ".lists.csv"
                        print(f"Writing to {filename}")
                    else:
                        print()
                    with smart_open(filename) as file:
                        for item in lists:
                            print(item, file=file)

                case "excel":
                    filename = parameters["filename"]
                    if filename:
                        filename += ".xlsx"
                    else:
                        filename = "address_book.xlsx"
                    print(f"Writing to {filename}")
                    oab2excel(data, filename)

                case "json":
                    filename = parameters["filename"]
                    if filename:
                        filename += ".json"
                        print(f"Writing to {filename}")
                    with smart_open(filename) as file:
                        print(
                            oab2json(
                                data,
                                compact=parameters["compact"],
                                indent=parameters["indent"],
                            ),
                            file=file
                        )

                case "table":
                    users, lists = oab2table(data, width=parameters["width"])
                    filename = parameters["filename"]
                    if filename:
                        filename += ".users.txt"
                        print(f"Writing to {filename}")
                    with smart_open(filename) as file:
                        print(users, file=file)

                    filename = parameters["filename"]
                    if filename:
                        filename += ".lists.txt"
                        print(f"Writing to {filename}")
                    else:
                        print()
                    with smart_open(filename) as file:
                        print(lists, file=file)

                case "txt":
                    filename = parameters["filename"]
                    if filename:
                        filename += ".txt"
                        print(f"Writing to {filename}")
                    with smart_open(filename) as file:
                        pprint.pprint(data, file)

                case "xml":
                    # Who cares ?
                    pass
        else:
            logging.error("'%s' is not a readable file", argument)
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
