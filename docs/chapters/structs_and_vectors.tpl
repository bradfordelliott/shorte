
@h3 @struct
The @struct tag defines a C style structure. It also supports generating
a picture showing the layout of the structure. The *title* attribute
should currently be a unique name since it is used to map any generated
image to the structure itself as well as generate C code from the structure
definition.

For example:

@shorte
\@struct: name="struct1" caption="blah blah" diagram="show:yes,align:128,bitorder:decrement"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Will generate:

@struct: name="struct1" caption="This is a caption. It is currently in the wrong place" diagram="show:yes,align:128,bitorder:decrement"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Another example:

@shorte
\@struct: name="struct2" caption="blah blah"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
Will generate a structure without a picture:

@struct: name="struct2" caption="This is a caption. It is currently in the wrong place"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@text
The bit order can also be reversed and the alignment can be changed:

@shorte
\@struct: name="struct3" caption="This is a caption. It is currently in the wrong place" diagram="show:yes,align:64,bitorder:increment"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@struct: name="struct3" caption="This is a caption. It is currently in the wrong place" diagram="show:yes,align:64,bitorder:increment"
--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number


@h3 @vector
The @vector is similar to the @struct tag and creates a bitfield type containing multiple fields.
Field sizes are generally outlined in bit ranges instead of bytes in the @struct tag. 

The following structure defines a 128 bit long bitfield with the bits shown in little endian
order on a 64 bit boundary.
<!--
@shorte
\@vector: name="vector1" caption="blah blah" diagram="show:yes,align:64,bitorder:increment"
--fields:
- Field  | Name       | Description
- 0-8    | Blah       | Blah blah
- 10     | *Reserved* | Reserved for future use
- 12     | My field   | da da da

- 32-63  | TBD        | Something here
- 64-127 | field2     | This is a description

@text
This renders to the following:

@vector: name="vector1" caption="" diagram="show:yes,align:64,bitorder:increment"
--fields:
- Field  | Name       | Description
- 0-8    | Blah       | Blah blah
- 10     | *Reserved* | Reserved for future use
- 12     | My field   | da da da

- 32-63  | TBD        | Something here
- 64-127 | field2     | This is a description

@text
This is an example of the Ethernet Header shown in little endian format:

@shorte
\@vector: name="Ethernet Header" caption="" diagram="show:yes,align:32,bitorder:decrement"
--fields:
- Field   | Name          | Description
- 0-47    | Dest Addr     | The destination MAC address
- 48-95   | Source Addr   | The source MAC address
- 96-111  | Ethernet Type | The ethernet type
- 112-159 | Data          | Variable length data field

@text
Which renders to:

@vector: name="Ethernet Header" caption="" diagram="show:yes,align:32,bitorder:decrement"
--fields:
- Field   | Name          | Description
- 0-47    | Dest Addr     | The destination MAC address
- 48-95   | Source Addr   | The source MAC address
- 96-111  | Ethernet Type | The ethernet type
- 112-159 | Data          | Variable length data field
-->
