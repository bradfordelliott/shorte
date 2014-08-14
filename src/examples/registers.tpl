@doctitle Code Samples
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah
@body
@h1 Registers
@struct: name="blah16" description="blah blah" private="False" diagram="show:yes,align:16,bitorder:increment"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | serial_number | The serial number of the device  
                          with some more description       | customer="CORTINA"
- 1x2   | blah          | A random field                   |
- 1x6   | blah2         | A random field                   |

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

@struct: name="clause45" description="Clause 45 address bits" diagram="show:yes,align:32,bitorder:decrement"
-- fields:
- Field | Name          | Description                      | Attributes
- 1x8   | Reserved      | Reserved for future use          |
- 1x8   | MMD           | The MMD section of clause 45     | 
- 1x16  | Address       | The address within the MMD       |

