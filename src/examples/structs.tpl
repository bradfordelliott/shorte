
@h1 Some Example Structures
@struct: name="blah2" description="blah blah" diagram="show:yes,align:64,bitorder:decrement"
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
- 4     | some_number   | Some random 4 byte number
-- inheritance:
- one
- two
    - three
        - four

