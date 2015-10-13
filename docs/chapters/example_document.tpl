@body

@h1 An Example Document
The following is an example that shows the structure
of a shorte document.

# This is an example of using python to load a shorte
# document from an external file.
<?
import os
# First create the output example as an inline HTML
# document
os.popen("../src/shorte.py -f ./shorte_example.tpl -p html_inline -o build-output/content/examples")

# Now load the source so it shows up in the document
handle = open("./shorte_example.tpl", "rt")
contents = handle.read()
handle.close()

contents = contents.replace("\n@", "\n\\@")
result = '''@shorte
%s''' % contents

# Finally add a link to the generated output
result += '''
@text
When shorte is executed with the following command
@bash
shorte.py -f shorte_example.tpl -p html_inline
@text
this will create a document that looks like [[examples/index.html]]
'''
?>
