
@h1 The Command Line
Here is the shorte command line
@bash
<?
import subprocess
phandle = subprocess.Popen(["../src/shorte", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
phandle.wait()
result = phandle.stdout.read()
result += phandle.stderr.read()
?>


@h2: if=0
Some Command Line Examples

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

