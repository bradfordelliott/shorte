@doctitle Wikiwords
@docsubtitle Wiki Word Highlighting

@docrevisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else
- 1.4.4   | 06 March, 2011 | This is a really long description of the version
                             change here and what changed in the document. It doesn't
                             match the format of the document but whatever.
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

@h2: wikiword="TestSection"
Test

This is a dummy header


@h1 This is some more data

See if TheseAreSomeWikiwords that will link up and These are some Wikiwords that won't link but [[->These are some Wikiwords]] will
also work as a link.

Want to make sure that Test doesn't link to the Test section but if I enter
TestSection it will link to the Test heading.


This is some random data

@h2: wikiword="ThePerformanceMonitor"
The Performance Monitor

This is a test of the word ThePerformanceMonitor and some more information
related to BlahBlahBlah

@h3: wikiword="BlahBlahBlah"
Blah Blah Blah

and some other random stuff here with a wiki link to TestSection