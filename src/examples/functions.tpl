@doctitle This is a really long title with some Function Examples
@docsubtitle Some Shorte Examples with a really long subtitle to ensure header doesn't wrap
@docnumber 23456

@body

@h2 Function Summary
@functionsummary

@h2 Type Summary
@typesummary

@h3 my_function
@prototype: language="c"
- function: my_function()
- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. 

    - It should support lists
        - And sub-items
    
    And new paragraphs.
    
        Indented text partially works but is not particularly
        robust.
        
        and it could use some work

    - Another list
        - With some more info

    @{table,
    -t An inlined table title
    -h Heading One | Heading Two
    -  Col 1       | Col 2
    -s Subheading 1
    -  Col 3       | Col 4
    }

- prototype:
    int my_function(int val1 [], int val2 [][5]);
- returns:
    TRUE on success, FALSE on failure
- params:
    -- val1 | I |
        1 = blah blah
            and more blah blah
            plus blah;
        
        2 = blah blah blah;
        
        0 = turn @{i,beacon} on
    -- val2 | I |
        *1* = blah blah
        
        *2* = blah blah blah

- example:
    rc = my_function(val);

    if(rc != 0)
    {
        printf("Uh oh, something bad happened!\n");
    }

- pseudocode:

    // Blah blah blah
    call_sub_function()

    if(blah)
    {
        // Do something else
        my_function();
    }
    

- see also:
    THis is a test

@h3 my_function2
@prototype:
- function: my_function2
- description:
    This is a description of my function with some more text
    and blah blah blah. I'm sure if I put enough text here then
    it will likely wrap but I'm not absolutely sure. We'll see
    what it looks like when it is actually formatted. For kicks
    we'll link to the EPT acronym
- prototype:
    cs_status my_function2(int val1 [], int val2 [][5]);
- returns:
    TRUE on success, FALSE on failure
- params:
    -- val1 | I |
        1 = blah blah
            and more blah blah
            plus blah;
        
        2 = blah @{u,blah blah};
        
        0 = turn @{hl,beacon} on
    -- val2 | I |
        *1* = blah blah
        
        *2* = blah blah blah


@h3 my_function3
@prototype:
- function: my_function3
- prototype:
    void my_function3(void)
- returns:
    None

