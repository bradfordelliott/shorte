@body

@h1 The Document Header
The first part of any Shorte document is the document header. It is
structured like HTML but isn't as strict. It is basically anything
in the document before the @body tag. An example document header looks like:

@shorte
# The beginning of the document is assumed to be the document
# header. As a convention normally the top level file will
# contain metadata about the document.

# The title of the document
\@doctitle The Shorte Language

# The subtitle of the document
\@docsubtitle Reference Manual

# A version number (can be overwritten from the command line)
\@docversion 1.0

# A number to assign to the document
\@docnumber 34567

\@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual


@h3 @doctitle
The @doctitle defines the title associated with the document. Only the first instance of this
tag is used. If another instance is encountered parsing the document it will be
ignored.

@shorte
# The document title
\@doctitle The Shorte Language

@h3 @docsubtitle
The @docsubtitle defines a subtitle for the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@shorte
# The document sub-title
\@docsubtitle Reference Manual

@h3 @docversion
The @docversion tag defines a version number for the document. This can be overridden
at the command line.

@h3 @docnumber
The @docnumber tag defines a number to associate with the document.

@h3 @docrevisions
The @docrevisions tag defines a revision history for the document. It's
syntax is similar to the @table tag.

@shorte
\@docrevisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual
- 1.0.1    | 09 July, 2013 | Another random update
