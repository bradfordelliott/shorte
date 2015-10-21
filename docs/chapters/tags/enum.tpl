@body
@h3 @enum
The @enum tag is used to define an enumeration.

@shorte
\@enum: name="e_my_test" caption="This is a test enum" description="This is a test enum"
--values:
- Name         | Value | Description
- SUPPLY_1V_TX | 0x0   |  1V supply TX 
- SUPPLY_1V_RX | 0x1   |  1V supply RX 
- SUPPLY_2p5V  | 0xf   |  2.5V supply 

@text
This generates the following snippet:

@enum: name="e_my_test" caption="This is a test enum" description="This is a test enum"
--values:
- Name         | Value | Description
- SUPPLY_1V_TX | 0x0   |  1V supply TX 
- SUPPLY_1V_RX | 0x1   |  1V supply RX 
- SUPPLY_2p5V  | 0xf   |  2.5V supply 
