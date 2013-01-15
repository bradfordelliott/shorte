
@h1 Sample
# In the table below we'll use the || sequence
# to span columns. The 'one' field will
# automatically span columns.
@struct: title="Indirect MDIO write" caption="Clause 45 MDIO Frame" diagram="show:yes,align:32,bitorder:increment"
- Field   | Name              | Description
- 4       | Preamble          | The 32 bit preamble consisting of all ones
- 2x1     | ST                | 00 - the start of frame
- 2x1     | 00                | OP Code
- 5x1     | PHYADD=MADDR      | PHYADD - PHYADD[4:2] must match the external MADDR[4:2] pins. PHYADD[1:0] are
                                used to select between the four slices.
- 5x1     | DEVADD=00000      | DEVADD - Not used in this device, must be set to 00000
- 2x1     | 10                | ...
- 16x1    | REGADDR           | The register address on the CS4321 device
-* Data Phase
-& 4      | Preamble          | The 32 bit preamble consisting of all ones
- 2x1     | ST                | 00 - the start of frame
- 2x1     | 01                | OP Code
- 5x1     | PHYADD=MADDR      | PHYADD - The physical slice of the device (0-3)
- 5x1     | DEVADD=00000      | DEVADD - Not used in this device, must be set to 00000
- 2x1     | 10                | ...
- 16x1    | REGDATA           | The register data on the CS4321 device
