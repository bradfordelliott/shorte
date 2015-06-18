@doctitle Wikiwords
@docsubtitle Wiki Word Highlighting

@docrevisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else
- 1.4.4   | 06 March, 2011 | This is a really long description of the version
                             change here and what changed in the document. It doesn't
                             match the format of the document but whatever.

# Inline the table of contents. Should probably
# have a check to see if the user entered an option at
# the command line and use that instead.
@doc.config html.inline_toc=1
@doc.config html.header_numbers=0

@doc.version 1.5

@body
# This is an example of assigning a wikiword to a heading.
# This is useful if you have a short heading and don't want
# the heading to be hyperlinked throughout the document or
# if you have a heading that has multiple words which aren't
# automatically hyperlinked.
@h1: wikiword="TheseAreSomeWikiwords"
These are some Wikiwords

@text
This is a test
This is another test

@h2: wikiword='''TestSection'''
Test Section

This is a dummy header

@h3 [[WikiTitle,Wiki Title]]
This is a better way of doing wikiwords. Shorte should support it now. I should see a link to WikiTitle
in the generated output.


@h1 This is some more data

See if TheseAreSomeWikiwords that will link up and These are some Wikiwords that won't link but [[@TheseAreSomeWikiwords, Some Wikiwords]] will
also work as a link.

Want to make sure that Test doesn't link to the Test section but if I enter
TestSection it will link to the Test heading. Also double check bug \#28 to ensure
that I can follow wikilinks with a period like TestSection.

This is some random data

This is another paragraph

And another paragraph

@h2: wikiword="ThePerformanceMonitor"
The Performance Monitor

This is a test of the word ThePerformanceMonitor and some more information
related to BlahBlahBlah

Some random other stuff

and still other stuff

@h3: wikiword="BlahBlahBlah"
Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

Blah Blah Blah

and some other random stuff here with a wiki link to TestSection and another link
to WikiTitle
