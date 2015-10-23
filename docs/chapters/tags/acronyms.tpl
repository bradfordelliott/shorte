@body

@h3 @acronyms
The @acronyms tag is format the same as @table except it always contains
two columns. The first column contains the acronym name, the second
column contains the acronym description. The description is in the format
of an @text block.

@acronyms
- Acronym | Definition
- ACRO1   | A first acronym
- ACRO2   | A second acronym that has some more detail with it like
            an ordered list:

            - abc
                - def
            - efg

@text
If you type ACRO1 it should be automatically cross referenced wherever it is used within
the document.
