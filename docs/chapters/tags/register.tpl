@body

@h3 @register
@shorte: exec="True"
\@register: name="clause45" diagram="show:yes,align:32,bitorder:decrement"
--description:
    This register defines the clause 45 address bits that are used by
    the software to do something random
    - one
      - two
    - three
    
    This is an additional paragraph if data describing the
    structure.

-- columns:
bits,name,description,customer

-- fields:
- Bits  | Name          | Description                  | Customer
- 8'b   | Reserved      | Reserved for future use      | INPHI
-
- 8'b   | MMD           | The MMD section of clause 45 | 
- 16'b  | Address       | The address within the MMD
                          - 1 = MMD 1
                              - 2 = MMD 2
                          - etc.   
