import xmlrpclib
import datetime

proxy = xmlrpclib.ServerProxy("http://127.0.0.1:8300")

contents = '''
@body
@h1 This is a test
This is some more data

@h3 This is another header
Blah blah blah
'''

settings = "html.header_numbers=0;html.inline_toc=0";

print proxy.parse(contents, "unstyled", settings)


