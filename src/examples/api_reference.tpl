@doctitle API Reference
@docsubtitle Example
@docnumber 1234
@docversion 0.1
@doc.footer.title My Footer
@doc.footer.subtitle My Subtitle

@body

@h1 API Reference Example
This might be an introduction to the code

# Now include the header file defining the sources. It may
# also have some markup in it.
@include "examples/test.h"


# Here is some more data
@h2 This is some more text here


@include "examples/test.c"

@acronyms
- Acronym | Definition
- EPT     | Egress Parser Table
- EPC     | Egress Parser CAM

@include "examples/test_python.py"
