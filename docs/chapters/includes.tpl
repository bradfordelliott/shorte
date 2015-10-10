
@h2 Include Files
Shorte supports include files using either of the following tags:

@table
- Include        | Description
- @include       | A normal include - interrupts any conditional text flow
- @include_child | A child include - obeys conditional text flow cascading rules

@h3 @include
The @include tag is used to include another file. This is to allow breaking
a document up into multiple modules. The @include will break any cascading of
conditional statements in the document hierarchy. For example, if you have this
code:

@shorte
\@h1: if="0"
Heading 1

\@include: "my_source_file.tpl"

@text
Then my_source_file.tpl will still be included as the @include tag will ignore the
condition on the previous heading. If you want my_source_file.tpl to be excluded
then the @include_child tag would be a better choice.

Includes also support conditionals in order to
support generating multiple documents from the same source. The example
below uses a command line define called *VARIABLE* to include
or exclude the file(s).

@shorte
\@include: if="VARIABLE == 'xyz'"
chapters/my_chapter.tpl
chapters/my_chapter2.tpl

@h3 @include_child
The @include_child tag is an alternative to the @include tag. It behaves
slightly differently in that it does not break the cascase of conditional
text but continues the current cascade.

@shorte
\@h1 My Title
This section will continue inside the my_chapter.tpl file.

\@include_child: if="VARIABLE == 'xyz'"
chapters/my_chapter.tpl
