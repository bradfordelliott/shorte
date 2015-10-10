@body

@h2 Heading Tags
Headings use the @hN format where *N* currently
ranges from 1-5.

@h3 @h1
The @h1 tag is the highest level header. It is similar in use
to the H1 tag from HTML.

@shorte
# An example header
\@h1 This is an example header
This is some text for the example header

# This header has some attributes associated with
# it so the header starts on the next line. The
# heading will included if MY_DEFINE is defined
# at the shorte command line.
\@h1: if="MY_DEFINE"
This Header is Conditional

The text for this heading starts here.


@h3 @h2
The @h2 tag is a hierarchial header directly beneath
the @h1 tag. It is similar to the H2 tag from HTML.

@shorte
\@h1 This is an example header

# An example second level header
\@h2 This is a sub header
This is some text related to the sub @h1 tag.

@h3 @h3
The @h3 tag is a hierarchial header directly beneath
the @h2 tag. It is similar to the H3 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header
Some text related to this header

@h3 @h4
The @h4 tag is a hierarchial header directly beneath
the @h3 tag. It is similar to the H4 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header

\@h4 This is a fourth level header
Some example text here

@h3 @h5
The @h5 tag is a hierarchial header directly beneath
the @h4 tag. It is similar to the H5 tag from HTML.

@shorte
\@h1 This is an example header

\@h2 This is a sub header

\@h3 This is a third level header

\@h4 This is a fourth level header

\@h5 This is a fifth level header
Some example text here

@h3 @h
The @h tag can be used to create a header that is
un-numbered.

@shorte
\@h This is an un-numbered header
Some random text after the header

@h3 Assigning Wikiwords
Sometimes it is desirable to assign wikiwords to a heading. This
allows multi-word headings to be automatically hyperlinked but also allows
the user to prevent a short heading from being automatically linked

There are two syntaxes for assigning wikiwords to headers. You can
use the *wikiword* attribute:

@shorte
\@h2: wikiword="MyHeading"
Test

This is some text associated with MyHeading. MyHeading will be expanded
to the word "Test" but Test won't get expanded.

@text
Or you can use an alternative syntax similar to many wiki
tools:

@shorte
\@h2 [[MyHeading, Test]]
This is some text associated with MyHeading. MyHeading will be expanded
to the word "Test" but Test won't get expanded.
