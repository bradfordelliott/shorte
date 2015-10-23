@body

@h3 @struct
The @struct tag defines a C style structure. It also supports generating
a picture showing the layout of the structure. The @{bold,name} attribute
should be unique name since it is used to map any generated
image to the structure itself as well as generate C code from the structure
definition.

An example is shown below:

@shorte: exec=True
\@text
The generated output from this example will look like:

\@struct: diagram="show:yes,align:128,bitorder:decrement"
--name:
struct1
--description:
This is a description of the structure that is in textblock
format so you can have

- a list
  - a sub list

or things like:

    an indented code block
    with more lines

or even a note
@{note,
This is my note here}

--fields:
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number


@text
#@text
#Will generate:
#
#@struct: name="struct1" caption="This is a caption. It is currently in the wrong place" diagram="show:yes,align:128,bitorder:decrement"
#--fields:
#- Field | Name          | Description
#- 8x8   | serial_number | The serial number of the device
#                          with some more description
#- 8x12  | part_number   | The part number of the device
#- 4     | some_number   | Some random 4 byte number

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
