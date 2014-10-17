@doctitle Include Tests

@body

@h1 @body
A random test

@h2 @tbd
A TBD

@h2 @brad
A non keyword

@h1 @include
This is a test

@h1 @include_child
@shorte
\@body
\@include "chapters/chapter_one.tpl"
\@include "chapters/chapter_two.tpl"

\@tbd

\@brad

\@body

\@include: if="ALLOW_CHAPTER3 == True"
chapters/chapter_three.tpl

# Here we'll use @body the @include_child tag since
# the @include tag normally breaks the flow of
# conditional statements. By using @include_child
# this file will only be included if ALLOW_CHAPTER3 == True
# @include_child "chapters/child_of_chapter_three.tpl"
