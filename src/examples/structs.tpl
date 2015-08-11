@doctitle Shorte Examples
@docsubtitle Structures


@include "examples/snippet_templates.tpl"
@body

@h1 Some Example Structures

@h2 Type Summary
@typesummary

@h2 Types
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

-- example: exec=True template=structs
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


@h4 blah3
@struct: diagram="show:yes,align:64,bitorder:increment"
--name:
blah3
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


