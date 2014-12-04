@doctitle Code Samples
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah
@body
@h1 Registers
@register: name="blah16" description="blah blah" private="False" diagram="width:600px;show:yes,align:16,bitorder:increment"
-- fields:
- Field | Name          | Description                      | Attributes
- 0-5   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 7     | blah          | A random field                   |
- 8-15  | blah2         | A random field                   |

@struct: name="blah16d" description="blah blah" private="False" diagram="show:yes,align:16,bitorder:decrement"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x2   | blah          | A random field                   |
- 1x6   | blah2         | A random field                   |


@struct: name="blah32" description="blah blah" private="False" diagram="show:yes,align:32,bitorder:increment"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x24  | blah2         | A random field                   |

@struct: name="blah32d" description="blah blah" private="False" diagram="show:yes,align:32,bitorder:decrement"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x24  | blah2         | A random field                   |


@struct: name="blah64" description="blah blah" private="False" diagram="show:yes,align:64,bitorder:increment"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x56  | blah2         | A random field                   |

@struct: name="blah64d" description="blah blah" private="False" diagram="show:yes,align:64,bitorder:decrement"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x56  | blah2         | A random field                   |

@h2 Register Definitions
This register definition should really look different than a structure
definition.

@register: name="clause45" description="Clause 45 address bits" diagram="show:yes,align:32,bitorder:decrement"
-- fields:
- Bits  | Name          | Description
- 8'b   | Reserved      | Reserved for future use
-
- 8'b   | MMD           | The MMD section of clause 45
- 16'b  | Address       | The address within the MMD


@struct: name="slice" diagram="show:yes,align:32"
-- fields:
- Bits   | Name             | Desc
- 1x24   | user_defined     | User defined bits of the API. These get passed through from
                              the *slice* parameter of higher level APIs and are typically
                              used to accesses multiple ASICs.
- 1x8    | channel_or_slice | The slice/port/channel of the device (0-7 duplex or 0-15 simplex)

