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
  (xx < 10) && yy
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

@h2 blah2
@struct: diagram="show:yes,align:64,bitorder:increment"
--name:
blah2
-- description:
This is a structure that contains some bitfields. It's
description can have a list:
- One
  - Two
    - Three
  - Four
-

And it can also have a new paragraph

-- fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 3     | some_number   | Some random 4 byte number
- 1x7   | some_bits     | A 7 bit field
- 1x1   | a_flag        | A 1 bit flag        
-- inheritance:
- one
- two
    - three
        - four

-- example:
  blah2 x;
  x.serial_number = "xxx";
  x.part_number = "yyy";

  printf("part_number = %s\n", x.part_number);

-- since:
This feature has been present since version 1.x.x

--see:
Also refer to structure xyz

--deprecated:
This structure is deprecated. You should figure out something else to use.

@h3 An Enum
@enum: name="e_my_test" description='''
This is a test enum
- A list entry
- Another list
    - Some more *info*
- Blah blah

Another paragraph
'''
-- values:
- Name                 | Value | Description
- VLT_SUPPLY_1V_TX     | 0x0   |  1V supply TX & some other info here
- VLT_SUPPLY_1V_RX     | 0x1   |  1V supply RX 
- VLT_SUPPLY_1V_CRE    | 0x2   |  1V supply digital core 
- VLT_SUPPLY_1V_DIG_RX | 0x3   |  1V supply digital RX 
- VLT_SUPPLY_1p8V_RX   | 0x4   |  1.8V supply RX 
- VLT_SUPPLY_1p8V_TX   | 0x5   |  1.8V supply TX 
- VLT_SUPPLY_2p5V      | 0xf   |  2.5V supply 
- VLT_SUPPLY_TP_P      | 0x9   |  Test point P 
- VLT_SUPPLY_TP_N      | 0x8   |  Test point N 
-- since:
Version 1.0
