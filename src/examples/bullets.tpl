@doctitle Shorte Examples
@docsubtitle Lists/Bullets 
@docversion 1.0
@body

@h1 List Tests

@h2 An Unordered List
Some text before the list that is really long and
probably wraps across multiple lines just to ensure that
the position of @{star,starred} text remains consistent.

@ul
- A
    - B
        - C
            -C1
            -C2
                -C2
            -C3
            -C4
                    -C3
                        -C4
    - D with some text
      wrapped across a line
    - E
        - F

@text
And some text after the list

@h2 An ordered list
Blah blah blah

@ol
- A
    - B
        - C
            -C1
                -C2
                    -C3
                        -C4
    - D with some text
      wrapped across a line
    - E
        - F
- one
- two
    - three
        -four
    - five
- six

@text
And blah blah blah

@h2 A paragraph test
This is some text with a list
- a
    - b
        -c
    - d
- e

@text
With some text that follows

@note
This is a note

with some more text
- and a list
- and another item
and still some more text

@note
This is another note

@question
This is a test

@warning
This is some random warning!

@note This is a third note

@tbd
This is TBD



@h2 Bullet Checks

@h3 Make sure this is a nested list
- Blah blah
    - Some indented blah blah

@h3 This should also have two levels
- One two three
    - One two three
      four five six


@h2 Checkboxes
This @{strike,section provides} some @{b,examples} of creating a list with
some checkboxes

-[ ] Not checked
-[x] checked
    -[ ] not checked
    -[x] checked
    - no checkbox
- This item has no checkbox
- Neither does this
-[a] An action
-[ax] A closed action

This is another example using the @ol tag:
@ol
-[]  Not checked
-[x] checked
    -[]  not checked
    -[x] checked
-[*] Starred
-[*x] Starred and checked
-[*a] Starred action
-[*ax] Starred complete action
-[1] low priority item
-[2] low priority item
-[3] low priority item
-[4a] Low priority action
-[5a] High @{starred, priority} action

@text
This is a final example using the @ul tag:

@ul
-[]  [[A link]]
-[x] checked
    -[]  not checked
    -[x] checked
- Priorities
    -[1] low priority item
    -[2] low priority item
    -[3] low priority item
    -[4a] Low priority action
    -[5a] High priority action
    -[1a*] Star @{star,overrides} priority


@text
A paragraph to end everything.
