@doctitle Code Samples
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah
@body
@h1 Registers
@register: name="blah16" description="blah blah" private="False" diagram="show:yes,align:16,bitorder:increment"
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
