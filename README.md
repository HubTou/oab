[![PyPI package](https://repology.org/badge/version-for-repo/pypi/python:oab.svg)](https://repology.org/project/python:oab/versions)
[![Servier Inspired](https://raw.githubusercontent.com/servierhub/.github/main/badges/inspired.svg)](https://github.com/ServierHub/)

# OAB

## NAME
oab - Microsoft Exchange/Outlook Offline Address Book (.oab files) decoder

## INSTALLATION
Once you have installed [Python](https://www.python.org/downloads/) v3.10+ and its packages manager [pip](https://pip.pypa.io/en/stable/installation/),
use the following command to install this tool:

```
pip install oab
```

## SYNOPSIS
**oab**
\[--bar|-b\]
\[--output|-o FILE\]
\[--csv|-C\]
\[--delimiter|-d CHAR\]
\[--excel|-E\]
\[--json|-J\]
\[--compact|-c\]
\[--ident|-i INT\]
\[--table|-T\]
\[--width|-w INT\]
\[--debug\]
\[--help|-?\]
\[--version\]
\[--\]
filename

## DESCRIPTION
The **oab** utility and library decode Microsoft Exchange/Outlook Offline Address Book (.oab) files,
and provide their contents as a Python dictionary or in CSV (delimiter separated values), Excel, JSON, text or tabular formats.

### Utility
By default, the utility will print the resulting Python dictionary to standard output as pretty printed text.

It is possible to get CSV, Excel, JSON and pretty table formats instead by using the *--csv|-C*, *--excel|-E*, *--json|-J* or *--table|-T* options.

For all these formats, the *--output|-o* option can be used to redirect output to file(s) with an argument indicating the desired basename.
**oab** will add the appropriate file extension and, in the case of CSV and pretty table formats, will separate the results in *users* and *lists* contents.

The delimiter used for CSV files can be changed from a comma to the argument of the *--delimiter|-d* option.

The style used for JSON files can be changed to compact mode with the *--compact|-c* option,
or with an indentation different from 4 spaces with the argument of the *--indent|-i* option.

The terminal width used for the pretty table files can be changed from the default 80 columns to the argument of the *--width|-w* option.
You should especially use this option when redirecting the program output to a file...

Last and least, you can disable the progress bar with the *--bar|-b* option.

### Python library
There are 5 public functions, one for loading an oab file,
the others for converting its result into another format:

```Python
import oab

data = oab.load_oab_file(filename, progress_bar=False)
# filename is a str. For example, "udetails.oab"
# the optional progress_bar is a bool
# data will be a dict

users, lists = oab.oab2csv(data, delimiter)
# delimiter is a str, normally for a single character
# users and lists will be list instances

oab.oab2excel(data, basename)
# basename is a str. For example, "address_book"

json_data = oab.oab2json(data, compact=False, indent=2)
# the optional compact is a bool
# the optional indent is an int. It's used when compact=False

users, lists = oab2table(data, width=173)
# the optional width is an int
# users and lists will be prettytable instances
```

### OPTIONS
Options | Use
------- | ---
--bar\|-b|Toggle OFF progress bar
--output\|-o FILE|Output result into FILE (extension added by oab)
--csv\|-C|Format results as CSV
--delimiter\|-d CHAR|Use CHAR as delimiter for CSV format
--excel\|-E|Format results as Excel tabbed file
--json\|-J|Format results as JSON
--compact\|-c|Use compact JSON format
--ident\|-i INT|Use INT spaces for indented JSON format
--table\|-T|Format results as tables
--width\|-w INT|Use INT columns in table format
--debug|Enable debug mode
--help\|-?|Print usage and a short help message and exit
--version|Print version and exit
--|Options processing terminator

## ENVIRONMENT
The COLUMNS environment variable will be used in tabular format if present
and output is not redirected to a file.

## EXIT STATUS
The **oab** utility exits 0 on success, and >0 if an error occurs.

## EXAMPLES
To generate pretty tables with relevant information about users and mailing lists in 2 files, use the following command:

<pre><samp>$ <kbd>oab --table --width 170 --output addressbook udetails.oab</kbd></samp></pre>

## SEE ALSO
### Specifications
* [Offline address books in Exchange Online](https://learn.microsoft.com/en-us/exchange/address-books/offline-address-books/offline-address-books)
* [Offline Address Book (OAB) File Format and Schema](https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxoab/b4750386-66ec-4e69-abb6-208dd131c7de)
* [Offline Address Book (OAB) Public Folder Retrieval Protocol](https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxpfoab/258a07a7-34a7-4373-87c1-cddf51447d00) - this last one is not used here as the tool works offline

### Other implementations
* SysTools [OAB Viewer](https://www.systoolsgroup.com/oab/viewer/)
* Mauville [OABtoCSV](https://github.com/Mauville/OABtoCSV)
* byteDJINN [BOA](https://github.com/byteDJINN/BOA)
* antimatter15 [boa](https://github.com/antimatter15/boa)

## STANDARDS
The **oab** utility is not a standard UNIX command.

This implementation tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## PORTABILITY
Tested OK under Windows.

## HISTORY
This program was made on a rainy sunday in order to investigate the contents of my Outlook .oab files.

It was then used to help cleaning my company's global address list.

## LICENSE
It is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou) and [Timothy Holmes](https://github.com/timothy-holmes).

This program is inspired by antimatter15's [boa](https://github.com/antimatter15/boa) and includes snippets of code from:
* [Mark@StackOverflow](https://stackoverflow.com/users/2606953/mark)
* [Wolph@StackOverflow](https://stackoverflow.com/users/54017/wolph)

## CAVEAT
Only version 4 full details files are fully supported at this time, whether compressed or not.

Some of the address books properties are undocumented and will appear as numbers.

## BUGS
Excel reports an error while opening generated XLSX files,
but after accepting its recovery offer these files appear to be fine...

## SECURITY CONSIDERATIONS
OAB files and the results generated by this program contain sensitive personal information
that should not be left unprotected.

There are known attacks in the wild targetting these files:
* [Attacking MS Exchange Web Interfaces](https://swarm.ptsecurity.com/attacking-ms-exchange-web-interfaces/)
* [Critical Microsoft Exchange Flaw: What is CVE-2021-26855?](https://www.upguard.com/blog/cve-2021-26855)
* grnbeltwarrior [OAB_Cleaver](https://github.com/grnbeltwarrior/OAB_Cleaver)

