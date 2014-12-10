@doctitle Code Samples
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah

@docrevisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else
- 1.4.4   | 06 March, 2011 | This is a really long description of the version
                             change here and what changed in the document. It doesn't
                             match the format of the document but whatever.

@body

@h1 A list of enums
This is a test of enums. Verify that all these are properly hyperlinked:
- VLT_SUPPLY_1V_TX
- VLT_SUPPLY_1V_RX
- VLT_SUPPLY_1V_CRE
- VLT_SUPPLY_1V_DIG_RX
- VLT_SUPPLY_1p8V_RX
- VLT_SUPPLY_1p8V_TX
- VLT_SUPPLY_2p5V
- VLT_SUPPLY_TP_P
- VLT_SUPPLY_TP_N

Also they should be hyperlinked in tables:

@table:
- Value
- VLT_SUPPLY_1V_TX
- VLT_SUPPLY_1V_RX
- VLT_SUPPLY_1V_CRE
- VLT_SUPPLY_1V_DIG_RX
- VLT_SUPPLY_1p8V_RX
- VLT_SUPPLY_1p8V_TX
- VLT_SUPPLY_2p5V
- VLT_SUPPLY_TP_P
- VLT_SUPPLY_TP_N

@h4 e_my_test
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

@h4 e_loopback

@enum: name="e_loopback" description='''
The loopback interface point
'''
-- values:
- Enum Name                | Enum Value | Enum Description
- LOOPBK_DUPLEX_NEAR_DATA  | 0x1        | Duplex Near data loopback
- LOOPBK_DUPLEX_FAR_DATA   | 0x2        | Duplex Far data loopback

        
@h4 e_loopback_interface

@enum: name="e_loopback_interface" description='''
The loopback interface
'''
-- values:
- Enum Name   | Enum Value | Enum Description
- LOOPBK_HOST | 0x1        | Loopback on the host interface
- LOOPBK_LINE | 0x3        | Loopback on the line interface

        
@h4 loopback_state_t

@struct: name="loopback_state_t" description='''
This structure is used to store state information
that is used when enabling the loopbacks.

- A list
    - With data
- And more data
- And some more stuff

And a new *paragraph*
'''
-- fields:
- Type           | Name | Description
- unsigned char  | initialized |  initialize flag 
- unsigned short | misc |
    The state of the misc register
    with a list
    - one
        - two
    - three

    and a new paragraph
- e_mode         | mode | A mode field

