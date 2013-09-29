
@h1 The Command Line
@bash
$ shorte.py -h
Usage: shorte.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILES, --files=FILES
                        The list of files to generate
  -l FILE_LIST, --list=FILE_LIST
                        The list of files to generate in an input file
  -o OUTPUT_DIR, --output=OUTPUT_DIR
                        The directory where output is generated
  -v VERSION, --version=VERSION
                        The version of the document
  -t THEME, --theme=THEME
                        The output theme
  -n NAME, --name=NAME  The document name or title
  -p PACKAGE, --package=PACKAGE
                        The output package. Supported types are html, odt,
                        word, and pdf
  -b OUTPUT_FORMAT, --output_format=OUTPUT_FORMAT
                        Set the output format in C generated code: bitfields,
                        byte_array, or defines
  -y, --diagnostic_code
                        Generate diagnostic code in generate code
  -c CONFIG, --config=CONFIG
                        The config file to load
  -s SETTINGS, --settings=SETTINGS
                        A list of settings to use that overrides the standard
                        config file
  -x PARSER, --parser=PARSER
                        The parser to use
  -a, --about           About this program
  -m MACROS, --macros=MACROS
                        Macro substitution
  -d DEFINE, --define=DEFINE
                        Macro substitution
  -r REPLACE, --search_and_replace=REPLACE
                        An input search and replace module that is loaded to
                        pre-process input files and replace any references

@h2 Some Command Line Examples

Parse a list of source files defined by source_file_list.py and generate
Shorte modules describing each of the source files.

@bash
shorte.py -l source_file_list.py -x cpp -p shorte -r bin/cs4224_snr.py -m 'SKU=CS4343;VERSION=1.1'; -o build-output/srcs

@text
- The *-r cs4224_snr.py* file allows a search and replace to be performed on the sources as they are
  generated.
- The *-m flag* passes a list of macros that can be used within the
  document for conditional inclusion or conditional text.
- The *-o build-output/srcs* parameter says to generate the files in the
  build-output/srcs directory.
- The *-x cpp* option switches the parser to the CPP parser instead of
  the default Shorte parser.
- The *-p shorte* parameter says to generate Shorte code from the C sources.

@text
The source_file_list.py file will look something like:

@python
result = '''
modules/high_level/cs4224.c
modules/high_level/cs4224.h

# Only include FC-AN and KR-AN in the duplex guide
if(SKU == 'CS4343'):
    result += '''
modules/kran/cs4224_kran.c
'''

@h2 Creating a Merge File
A merge file re-assembles a Shorte document into a single file

