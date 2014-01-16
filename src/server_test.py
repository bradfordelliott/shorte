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

print proxy.parse(contents, "shorte")


