@doctitle Defines
@docsubtitle Code Constructs
@body

@h1 Defines
@define
--name:
  test1
--description:
    This is a description of my define here that includes
    an inline table:

    @{table,
    -h One | Two
    -  Three | Four
    -s Five
    -  Six   | Seven
    }

    and an inline note:

    @{note,
    This is some random information here
    }

    as well as a TBD:
    
    @{tbd,
    This info is TBD
    }

--value:
  1
--since:
  Introduced in release 1.0
--see:
  blah,blah,blah
--example:
  int blah = test1;
--requires:
  This define is only present if PC_FLAG == 1

@h2 define2
@define
--name:
  define2
--description:
  This is a random description of this define
  with some more data here.
--value:
  This is my define2
--deprecated:
  This define was deprecated some time ago. You
  should find another define to use.
