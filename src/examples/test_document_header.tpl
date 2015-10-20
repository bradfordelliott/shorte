@doc.title Shorte
@doc.subtitle Document Header
@doc.version 1.0

@doc.number 1234

@doc.revisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else

@doc.author Brad Elliott

# Override the shorte configuration in the document itself
@doc.config shorte.theme=inphi

# The document footer
@doc.footer.title Footer
@doc.footer.subtitle Footer Subtitle

@doc.info
I don't this property is currently used. It should probably be
formatted as if were a textblock.

# This is an example of a snippet that can be used when executing
# code examples.
@doc.template: name="2"
import sys
print "Hello $1"

# Change the output directory from the default of build-output
#@doc.outdir build-output

# Change the name of the output file. This doesn't seem to work.
@doc.filename user_guide.html


@body

@h1 Testing the Document Header
This is just a test file for testing the shorte document header.

@h2 This is another random heading
With some text
