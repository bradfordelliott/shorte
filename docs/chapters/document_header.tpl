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
\@doc.title The Shorte Language

# The subtitle of the document
\@doc.subtitle Reference Manual

# A version number (can be overwritten from the command line)
\@doc.version 1.0

# A number to assign to the document
\@doc.number 34567

\@doc.revisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual


@h3 [[TagDocTitle, @doc.title]]
The TagDocTitle defines the title associated with the document. Only the first instance of this
tag is used. If another instance is encountered parsing the document it will be
ignored.

@shorte
# The document title
\@doc.title The Shorte Language

@h3 [[TagDocSubtitle, @doc.subtitle]]
The TagDocSubtitle defines a subtitle for the document. Only the first instance of this
tag is used. If a second instance is encountered it will be ignored.

@shorte
# The document sub-title
\@doc.subtitle Reference Manual

@h3 [[TagDocVersion, @doc.version]]
The TagDocVersion tag defines a version string for the document. This can be overridden
at the command line using the @{bold,-version} command line option.

@h3 [[TagDocNumber, @doc.number]]
The TagDocNumber tag defines a number to associate with the document. This is used in some
output templates to uniquely identify the document.

@h3 [[TagDocRevisions, @doc.revisions]]
The TagDocRevisions tag defines a revision history for the document. It's
syntax is similar to the @table tag.

@shorte
\@doc.revisions:
- Revision | Date          | Description
- 1.0.0    | 08 July, 2013 | Initial draft of the Shorte Reference Manual
- 1.0.1    | 09 July, 2013 | Another random update
