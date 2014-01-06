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

@h4 e_my_test
@enum: name="e_my_test" caption='''
This is a test enum
- A list entry
- Another list
    - Some more *info*
- Blah blah

Another paragraph
'''
- Name                       | Value | Description
- LEEDS_VLT_SUPPLY_1V_TX     | 0x0   |  1V supply TX 
- LEEDS_VLT_SUPPLY_1V_RX     | 0x1   |  1V supply RX 
- LEEDS_VLT_SUPPLY_1V_CRE    | 0x2   |  1V supply digital core 
- LEEDS_VLT_SUPPLY_1V_DIG_RX | 0x3   |  1V supply digital RX 
- LEEDS_VLT_SUPPLY_1p8V_RX   | 0x4   |  1.8V supply RX 
- LEEDS_VLT_SUPPLY_1p8V_TX   | 0x5   |  1.8V supply TX 
- LEEDS_VLT_SUPPLY_2p5V      | 0xf   |  2.5V supply 
- LEEDS_VLT_SUPPLY_TP_P      | 0x9   |  Test point P 
- LEEDS_VLT_SUPPLY_TP_N      | 0x8   |  Test point N 

@h4 e_cs4224_loopback

@enum: name="e_cs4224_loopback" caption='''
The loopback interface point
'''
- Enum Name                       | Enum Value | Enum Description
- CS4224_LOOPBK_DIGITAL_NEAR_DATA | 0x1        | Digital Near data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_NEAR_DATA
- CS4224_LOOPBK_DUPLEX_NEAR_DATA  | 0x1        | Duplex Near data loopback
- CS4224_LOOPBK_DIGITAL_FAR_DATA  | 0x2        | Digital Far data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_FAR_DATA
- CS4224_LOOPBK_DUPLEX_FAR_DATA   | 0x2        | Duplex Far data loopback

        
@h4 e_cs4224_loopback_interface

@enum: name="e_cs4224_loopback_interface" caption='''
The loopback interface
'''
- Enum Name          | Enum Value | Enum Description
- CS4224_LOOPBK_HOST | 0x1        | Loopback on the host interface
- CS4224_LOOPBK_LINE | 0x3        | Loopback on the line interface

        
@h4 cs4224_diags_duplex_loopback_state_t

@struct: name="cs4224_diags_duplex_loopback_state_t" title="cs4224_diags_duplex_loopback_state_t" caption='''
This structure is used to store state information
that is used when enabling the line or host side duplex
near or far loopbacks.

- A list
    - With data
- And more data
- And some more stuff

And a new *paragraph*
'''
- Type | Name | Description
- cs_uint8 | initialized |  initialize flag 
- cs_uint16 | stx0_misc |
    The state of the SDS_COMMON_STX0_MISC register 
    with a list
    - one
        - two
    - three

    and a new paragraph
- cs_uint16 | line_mseq_power_down |  The state of the line SDS_DSP_MSEQ_POWER_DOWN_LSB register 
- cs_uint16 | host_mseq_power_down |  The state of the host SDS_DSP_MSEQ_POWER_DOWN_LSB register 
- cs_uint16 | rx0_config |  The state of the SDS_COMMON_RX0_Config register 
- cs_uint16 | tx0_config |  The state of the SDS_COMMON_TX0_Config register 
- cs_uint16 | line_clkout_ctrl |  The state of the line SDS_COMMON_SRX0_RX_CLKOUT_CTRL register 
- cs_uint16 | host_clkout_ctrl |  The state of the host SDS_COMMON_SRX0_RX_CLKOUT_CTRL register 
- cs_uint16 | clkdiv_ctrl |  The state of the SDS_COMMON_SRX0_RX_CLKDIV_CTRL register 
- cs_uint16 | rxlockd0_ctrl |  The state of the SDS_COMMON_RXLOCKD0_CONTROL register 
- cs_uint16 | line_spare12 |  The state of the LINE_SDS_DSP_MSEQ_SPARE12_LSB register 
- cs_uint16 | host_spare12 |  The state of the HOST_SDS_DSP_MSEQ_SPARE12_LSB register 
- cs_uint16 | mseq_options |  The state of the SDS_DSP_MSEQ_OPTIONS_SHADOW register 
- e_cs4224_edc_mode | line_edc_mode |  The state of the line EDC mode 
- e_cs4224_edc_mode | host_edc_mode |  The state of the host EDC mode 

