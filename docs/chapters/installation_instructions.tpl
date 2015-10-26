
@h1 Installation Instructions

@h2 Installing on Windows
To install on Windows the easiest thing to do is to download a
pre-compiled build of Shorte. This uses Py2exe to generate an
executable version of the tool rather than requiring Python be
installed on the system. The latest windows build can be downloaded
from:

  [[http://home-ott/~belliott/projects/shorte/releases/win32]]

@h2 Installing on Linux

@h3 From a pre-built Binary
The latest 64 bit linux build can be downloaded from:
from:

  [[http://home-ott/~belliott/projects/shorte/releases/linux64]]

@h3 From Source
To install from sources several prerequisites are required.
They are shown in the following table:
@table: title="Installation prerequisites"
- Tool   | Tool Version        | Description
- GCC    | \3.4 or later       | A compiler used to compile the cairo plugin for Python
- Make   | \3.81 or later      | In order to run the makefile associated with the cairo plugin
- Cairo  | \1.11 or later      | Cairo is required for generating images such as structure definitions
                                or sequence diagrams.
- SWIG   | \2.0 or later       | SWIG is required in order to build the cairo plugin for Python.
- Python | \2.6 or 2.7         | Shorte is built in Python. Version 2.6 or later is required but 3.x
                                is currently not supported.
- Py2exe | Version for Python  | This tool is used to generate

@h2 Changing the Path to LibreOffice/OpenOffice
In order to generate PDF documents it is necessary to modify the shorte.cfg file to setup
the path to OpenOffice/LibreOffice. This may be done the following field in the config file:

@code
# Paths to open office swriter
path.oowriter.win32=C:/Program Files/LibreOffice 4/program/swriter.exe
path.oowriter.linux=/home/belliott/libreoffice/opt/libreoffice4.1/program/swriter
path.oowriter.osx=/Applications/LibreOffice.app/Contents/MacOS/soffice



@h2 Setting up LibreOffice/OpenOffice
Shorte currently uses LibreOffice or OpenOffice for generating PDF
or ODT documents. To do this it runs a conversion script convert_to_pdf.odt.
This script handles updating the table of contents and converting the
document to a PDF.

To run the script OpenOffice/LibreOffice must be setup to run scripts
from the following directory:

@pre
${path_to_shorte}/templates/odt

@text
Instructions to do this are shown below.

@h Change the Macro Permissions for running convert_to_pdf.odt
First open OpenOffice/LibreOffice writer and select *options" from the *Tools* menu:

<<chapters/images/swriter_tools_menu.png>>

Under LibreOffice/OpenOffice select *Security* to bringup the *Macro Security* settings. Press
the *Macro Security* button  

<<chapters/images/swriter_tools_menu_macro_security.png>>

Change the macro security to *High* and then click on the *Trusted Sources* tab to
add shorte to the path.

<<chapters/images/swriter_tools_menu_macro_security_high.png>>

In the *Macro Security* dialog under the *Trusted Sources* tab click *Add* to
add Shorte to the path.

<<chapters/images/swriter_tools_menu_macro_security_high_setup_path.png>> 

