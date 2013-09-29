
@h1 Test Cases
Shorte allows the creation of test reports that include a summary section
which links to the results of a particular test case defined by the @testcase tag.

@h3 @testcasesummary
The @testcasesummary creates a summary of all the test cases defined in
the document.

Adding this block of code:

@shorte
\@testcasesummary

@text
Will expand to:

@testcasesummary


@h3 @testcase
The @testcase tag is used to define information about a testcase.
It looks something like this:

@shorte
\@testcase
:name: Version
:desc:
This is a diagnostic method that is used to retrieve the
API version information. It reads the version string from the API
and does a very simple check to validate the sanity of the
version string.

:status: PASSED
:duration: 0.100000 sec

\@testcase
:name: Register test
:desc:
This test validates basic register access
by reading the ASIC IDs and verifying the match the
expected value.

:status: PASSED
:duration: 10.480000 sec


\@testcase
:name: Register dump test
:desc:
This test validates the register dump
from the API. Due to restrictions in SWIG it is impossible
to test all the methods so it uses a high-level print
method to display the register dump.

:status: PASSED
:duration: 11.760000 sec

@text
When rendered these examples look like:

@testcase
:name: Version
:desc:
This is a diagnostic method that is used to retrieve the
API version information. It reads the version string from the API
and does a very simple check to validate the sanity of the
version string.

:status: PASSED
:duration: 0.100000 sec


@testcase
:name: Register test
:desc:
This test validates basic register access
by reading the ASIC IDs and verifying the match the
expected value.

:status: PASSED
:duration: 10.480000 sec


@testcase
:name: Register dump test
:desc:
This test validates the register dump
from the API. Due to restrictions in SWIG it is impossible
to test all the methods so it uses a high-level print
method to display the register dump.

:status: PASSED
:duration: 11.760000 sec

