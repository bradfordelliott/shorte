@doctitle Shorte Documentation Tool
@doctitle Installation Instructions for Shorte

@body
@h1 Installation Instructions

The following table lists the prerequisites for building/running
the Shorte tool.
@table: title="Installation prerequisites"
- Cairo  | Version        | Description
- SWIG   |                |
- Python | 2.6 or 2.7     | 
- Py2exe | ver for Python | This tool is used to generate

@h2 Setting up LibreOffice/OpenOffice
Shorte currently uses LibreOffice or OpenOffice for generating PDF
or ODT documents. To do this it runs a conversion script convert_to_pdf.odt.
This script handles updating the table of contents and converting the
document to a PDF.

To run the script OpenOffice/LibreOffice must be setup to run scripts
from the following directory:

${path_to_shorte}/templates/odt

Instructions to do this are shown below.


