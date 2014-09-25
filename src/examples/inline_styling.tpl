@doctitle Inline Styling
@docsubtitle Examples

@body

@h1 Inline Styling
This example attempts to describe the usage of inline styling. This stying is
part of every text block and can be used for simple styling like @{b, bold text} or @{i, italic text}.
You can @{strike, strike text out}, @{u, underline} things, @{star, star them}, @{hl, highlight things}.

You can also create more complex things like tables:

@{table,
-t Table Title
-h Heading One ! Heading Two
- Data One ! Data Two
}

You can also create notes @{note, This is my note}

Create pre text
@{pre,
This is some <pre> text similar to HTML
}

Create an image
@{image, src="examples/record_0.png"}

And some more other fancy stuff!!!

This is a @{complete, some completed text}

This is a @{tbd, TBD section}

This is a @{warning, warning}

This is a @{question, question}

@h2 Broken Parsing
The following table doesn't currently parse correctly. The table runs into the note and
parsing breaks down.

@table
- Application               | Description
- CS_HSIO_EDC_MODE_CX1      | Configure the microcode to support CX1/Direct Attach cables.
                              @{table,
                              -h Supported Data Rates
                              -s Min     ! Max       ! Note
                              - 9.8Gbps  ! <10.6Gbps ! API Optimized range
                              - 10.6Gbps ! <11.3Gbps ! Optional tuning could be applied to improve performance.
                              - 11.3Gbps ! <12.5Gbps ! Optional tuning could be applied to improve performance.
                              }
- CS_HSIO_EDC_MODE_SR       | Configure the microcode to support SFP+ modules
                              that use a limiting post amplifier. This mode should be selected
                              when running at data rates < 8.5Gbps in addition to disabling
                              power savings.
                              @{table,
                              -h Supported Data Rates
                              -s Min    ! Max     ! Note
                              - 622Mbps ! 15Gbps  ! API Optimized range
                              }

                              @{note,
                              Further receiver tuning required to compensate for trace loss between
                              the transceiver and the pins of the ASIC. See this rule:
     
                              - rules.rx_if.dplx_line_eq (Duplex devices)
                              - rules.rx_if.dplx_host_eq (Duplex devices)
                              - rules.rx_if.splx_eq      (Simplex devices)
                              }


