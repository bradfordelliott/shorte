@body
@h1 test.c
@h CursorKind.MACRO_DEFINITION @test.c => None
@define: file=test.c line=37
--name: FALSE
--description:
    This is an example of a define

--value:
     0


@h CursorKind.MACRO_DEFINITION @test.c => None
@define: file=test.c line=43
--name: TRUE
--description:
    This is another define that is the opposite
    of FALSE

--value:
     !FALSE


@h CursorKind.MACRO_DEFINITION @test.c => None
@define: file=test.c line=92
--name: TEST_DOT_C_BLAH_BLAH_BLAH
--description:
    Another define
    with a multi-line description
    and a "quote" built-in

--value:
     "This is my define here"


@h CursorKind.MACRO_INSTANTIATION @test.c => None
@h CursorKind.ENUM_DECL @test.c => 
@enum: file=test.c line=122
--name:  e_test_dot_c_blah
--description:
    This enum description has a list in it
    - one
      - two
      - three
    - four
    
    This is a new parapraph
    
    @{table,
    -t One
    -  Three ! Four
    }
    
    and a new paragraph
    
    @{table,
    -x Another table
    -r A reserved row
    -  This is a test
    }
    
    @{tbd,
    This still needs to be done}
    
    

-- values:
- Enum Name | Enum Value | Enum Description

- xxx | 1 |
    Some description of a
    with a list
    - One
      - Two
      - Three
    - Four
    
    and a table:
    
    @{table,
    -x One   ! two
    -  Three ! Four
    }

- yyy | 2 |
    Some value for b


@h CursorKind.ENUM_CONSTANT_DECL @test.c => xxx
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => yyy
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.TYPEDEF_DECL @test.c => e_test_dot_c_blah
@h CursorKind.ENUM_DECL @test.c => 
@enum: file=test.c line=122
--name:  e_test_dot_c_blah
--description:
    This enum description has a list in it
    - one
      - two
      - three
    - four
    
    This is a new parapraph
    
    @{table,
    -t One
    -  Three ! Four
    }
    
    and a new paragraph
    
    @{table,
    -x Another table
    -r A reserved row
    -  This is a test
    }
    
    @{tbd,
    This still needs to be done}
    
    

-- values:
- Enum Name | Enum Value | Enum Description

- xxx | 1 |
    Some description of a
    with a list
    - One
      - Two
      - Three
    - Four
    
    and a table:
    
    @{table,
    -x One   ! two
    -  Three ! Four
    }

- yyy | 2 |
    Some value for b


@h CursorKind.ENUM_CONSTANT_DECL @test.c => xxx
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => yyy
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.STRUCT_DECL @test.c => 
@struct: file=test.c line=157
--name:  test_dot_c_mystruct_t
--description:
    This is a description of mystruct
    
    @{warning,
    This is a warning inside the structure
    description}
    
    

-- fields:
- Type | Name | Description
- int | a |
    This is a description of the field 'a'


- char * | b |
    This is a description of field 'b'



@h CursorKind.FIELD_DECL @test.c => a
@h CursorKind.FIELD_DECL @test.c => b
@h CursorKind.TYPEDEF_DECL @test.c => test_dot_c_mystruct_t
@h CursorKind.STRUCT_DECL @test.c => 
@struct: file=test.c line=157
--name:  test_dot_c_mystruct_t
--description:
    This is a description of mystruct
    
    @{warning,
    This is a warning inside the structure
    description}
    
    

-- fields:
- Type | Name | Description
- int | a |
    This is a description of the field 'a'


- char * | b |
    This is a description of field 'b'



@h CursorKind.FIELD_DECL @test.c => a
@h CursorKind.FIELD_DECL @test.c => b
@h CursorKind.STRUCT_DECL @test.c => 
@struct: file=test.c line=170
--name:  test_dot_c_mystruct2_t
--description:
    THis is a test
    
    

-- fields:
- Type | Name | Description
- int | y |
    Test



@h CursorKind.FIELD_DECL @test.c => y
@h CursorKind.TYPEDEF_DECL @test.c => test_dot_c_mystruct2_t
@h CursorKind.STRUCT_DECL @test.c => 
@struct: file=test.c line=170
--name:  test_dot_c_mystruct2_t
--description:
    THis is a test
    
    

-- fields:
- Type | Name | Description
- int | y |
    Test



@h CursorKind.FIELD_DECL @test.c => y
@h CursorKind.ENUM_DECL @test.c => 
@enum: file=test.c line=207
--name:  e_test_dot_c_cs4224_prbs_polynomial
--description:
    The supported PRBS polynomials 
    
    With a list
    - one
      - two
    - three
    - four
    
    And another paragraph
    
    And still another paragraph
    
    And a new list
    
    - a new list
      - a list item
    
    Some @{i, italic text} and some @{b, bold text}.
    
    @{note,
        This should be a note
        with a list inside of it but it probably doesn't
        work.
        
        - one
        - two
        - three
    }

-- values:
- Enum Name | Enum Value | Enum Description

- CS4224_PRBS_Tx_2exp31 | 0 |
    1 + x^28 + x^31
    - a list
      - a subitem
    - Some *bold* data
    
    A new paragraph

- CS4224_PRBS_Tx_2exp23 | 1 |
    1 + x^18 + x^23
    
    With a table
    
    @{table,
    - One  ! Two  ! Three
    - Four ! Five ! Six
    }

- CS4224_PRBS_Tx_2exp15 | 2 |
    1 + x^14 + x^15
    
    @{note, Should not really use this. This should be a list but it doesn't appear to work.
    
     - one
     - two
     }

- CS4224_PRBS_Tx_2exp7 | 3 |
    1 + x^6 + x^7

- CS4224_PRBS_Tx_2exp9 | 4 |
    1 + x^4 + x^9

- CS4224_PRBS_Tx_2exp9_5 | 5 |
    1 + x^5 + x^9

- CS4224_PRBS_Tx_2exp58 | 6 |
    1 + x^5 + x^58


@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp31
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp23
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp15
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp7
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp9
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp9_5
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp58
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.TYPEDEF_DECL @test.c => e_test_dot_c_cs4224_prbs_polynomial
@h CursorKind.ENUM_DECL @test.c => 
@enum: file=test.c line=207
--name:  e_test_dot_c_cs4224_prbs_polynomial
--description:
    The supported PRBS polynomials 
    
    With a list
    - one
      - two
    - three
    - four
    
    And another paragraph
    
    And still another paragraph
    
    And a new list
    
    - a new list
      - a list item
    
    Some @{i, italic text} and some @{b, bold text}.
    
    @{note,
        This should be a note
        with a list inside of it but it probably doesn't
        work.
        
        - one
        - two
        - three
    }

-- values:
- Enum Name | Enum Value | Enum Description

- CS4224_PRBS_Tx_2exp31 | 0 |
    1 + x^28 + x^31
    - a list
      - a subitem
    - Some *bold* data
    
    A new paragraph

- CS4224_PRBS_Tx_2exp23 | 1 |
    1 + x^18 + x^23
    
    With a table
    
    @{table,
    - One  ! Two  ! Three
    - Four ! Five ! Six
    }

- CS4224_PRBS_Tx_2exp15 | 2 |
    1 + x^14 + x^15
    
    @{note, Should not really use this. This should be a list but it doesn't appear to work.
    
     - one
     - two
     }

- CS4224_PRBS_Tx_2exp7 | 3 |
    1 + x^6 + x^7

- CS4224_PRBS_Tx_2exp9 | 4 |
    1 + x^4 + x^9

- CS4224_PRBS_Tx_2exp9_5 | 5 |
    1 + x^5 + x^9

- CS4224_PRBS_Tx_2exp58 | 6 |
    1 + x^5 + x^58


@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp31
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp23
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp15
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp7
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp9
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp9_5
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.ENUM_CONSTANT_DECL @test.c => CS4224_PRBS_Tx_2exp58
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.FUNCTION_DECL @test.c => test_dot_c_my_test
@prototype: language="c" file=test.c line=320
--function: test_dot_c_my_test
--prototype:
    int test_dot_c_my_test(int blah,int * dummy);
--description:
    This is a description of my function
    
    With another line here and some *bold* text.
    
    And a table
    @{table,
    - One  ! Two  ! Three
    - Four ! Five ! Six
    }
    
    @{question,
    What should I do here?}
    
    @{note,
    This is a random note here that contains a list
    - one
        - two
    -}
    
    

--returns:
    TRUE on success, FALSE on failure.


--params:
  -- blah | I | 
    Some data associated with blah
    with some more data

    @{table,
    - One   ! Two
    - Three ! Four
    }

    and a note

    @{note,
    - This is a note that is really a list
    }

    This is more @{b,data}.



  -- dummy | O | Some other dumb variable.



--example:

    0         1         2         3         4         5         6         7
    01234567890123456789012345678901234567890123456789012345678901234567890123456789
    int blah = 0;
    int dummy = TRUE;

    // The text doesn't work properly and comments
    // aren't showing up in the parsed text
    dummy = blah;

    if(1)
    {
        my_test(blah,dummy);
    }


--see also:
    
    test_dot_c_my_test21



@h CursorKind.PARM_DECL @test.c => blah
@h CursorKind.PARM_DECL @test.c => dummy
@h CursorKind.COMPOUND_STMT @test.c => None
@h CursorKind.RETURN_STMT @test.c => None
@h CursorKind.UNARY_OPERATOR @test.c => None
@h CursorKind.INTEGER_LITERAL @test.c => None
@h CursorKind.FUNCTION_DECL @test.c => test_dot_c_my_test21
@prototype: language="c" file=test.c line=355
--function: test_dot_c_my_test21
--prototype:
    int test_dot_c_my_test21(int blah);
--description:
    This is another test function
    
    

--returns:
    Always returns FALSE.


--params:
  -- blah | I | This is a test



--example:
: if("DEFINE1")
Include this example only if DEFINE1 is set



@h CursorKind.PARM_DECL @test.c => blah
@h CursorKind.COMPOUND_STMT @test.c => None
@h CursorKind.FUNCTION_DECL @test.c => just_a_prototype
@prototype: language="c" file=test.c line=366
--function: just_a_prototype
--prototype:
    int just_a_prototype(int x,int y);
--description:
    This is a prototype method
    
    

--returns:
    A description of the return code.
--params:

@h CursorKind.PARM_DECL @test.c => x
@h CursorKind.PARM_DECL @test.c => y
@h CursorKind.FUNCTION_DECL @test.c => test_dot_c_my_undocumented_function
@h CursorKind.PARM_DECL @test.c => main
@h CursorKind.COMPOUND_STMT @test.c => None
@h CursorKind.FUNCTION_DECL @test.c => test_dot_c_my_private_function
@h CursorKind.COMPOUND_STMT @test.c => None
@h CursorKind.FUNCTION_DECL @test.c => main
@h CursorKind.COMPOUND_STMT @test.c => None
@h CursorKind.RETURN_STMT @test.c => None
@h CursorKind.INTEGER_LITERAL @test.c => None
