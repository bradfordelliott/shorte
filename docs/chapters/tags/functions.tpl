
@h3 @prototype
The @prototype is used to describe a function prototype. This might be used
when architecting code or it can also be extracted from existing source code (Currently
only C sources can be parsed).

When rendered it will create output with it's own header automatically
added for wiki linking. This behavior
may be controlled by the @{b,prototype_add_header} field in the Shorte config file.

@shorte: exec=True
\@prototype: language="c"
-- function: my_function
-- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
-- prototype:
    int my_function(int val1 [], int val2 [][5]);
-- returns:
    TRUE on success, FALSE on failure
-- params:
    -- val1 | I | 
            1 = blah blah
                and more blah blah
                plus blah

            2 = blah blah blah

            0 = turn beacon on
    -- val2 | I |
            *1* = blah blah

            *2* = blah blah blah
-- example:
    rc = my_function(val);

    if(rc != 0)
    {
        printf("Uh oh, something bad happened!\n");
    }

-- pseudocode:

    // Blah blah blah
    _call_sub_function()

    if(blah)
    {
        // Do something else
        _call_sub_function2()
    }
    
-- see also:
    THis is a test

@h3 @functionsummary
The @functionsummary tag creates a summary table of all prototypes
cross referenced or defined within the document. In this document we've
defined a single prototype my_function which should show up
automatically when this tag is inserted into the document. Additionally
if source code is included any prototypes would automatically get picked
up in this table.

@shorte
\@functionsummary

@text
Generates:

@functionsummary


@h3 @typesummary
The @typesummary tag creates a summary of all structures or enumerations
defined within the document or in any parsed source code.

@shorte
\@typesummary

@text
Generates:

@typesummary
