import sys
sys.path.append(".")

import unittest

from src.shorte_defines import *

class test_string_handling(unittest.TestCase):

    def setUp(self):
        pass


    def test_indentation(self):
        '''Test string indentation handling methods'''

        source = '''@def
    """This is a test method"""
    print "Hello world!"
    '''
        
        expected = '''@def
    """This is a test method"""
    print "Hello world!"'''

        output = trim_leading_indent(source, allow_second_line_indent_check=False)

        self.assertEqual(output, expected)
        

        source = '''    @def myfunc():
        """This is another test"""
        print "Hello2!"
        '''
        
        expected = '''@def myfunc():
    """This is another test"""
    print "Hello2!"'''

        output = trim_leading_indent(source, allow_second_line_indent_check=False)

        self.assertEqual(output, expected)

        source = '''This is my test
            with a block like this
            and some more random data
            and blah blah. The final line
              has more indentation'''

        expected = '''This is my test
with a block like this
and some more random data
and blah blah. The final line
  has more indentation'''

        output = trim_leading_indent(source)
        
        self.assertEqual(output, expected)


        source = '''

  this is not blank
neither is this

'''
        expected = '''  this is not blank
neither is this
'''

        output = trim_blank_lines(source)

        self.assertEqual(output, expected)

unittest.main()
