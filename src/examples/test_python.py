'''
@h1: wikiword=RandomData
This is some random data here

With some more text in it.

@python: exec=True
import sys
sys.path.append('./examples')
from test_python import *
hello()
world()
'''

class myclass(object):
    '''This is a description of the class with
       a table.
       
       @{table,
       - One | Two
       - Three | Four
       }
    '''

    def __init__(self):
        '''The constructor for the myclass object'''
        print "Calling __init__"

    def hello(self):
        print "Hello myclass!"

    def __str__(self):
        '''Convert the myclass object into a string

           return The class instance as a string
        '''
        output = 'myclass'
        return output


def hello(p1=None, p2=None, p3=True):
    '''@h1 [[WikiWord,This is a random heading]]
       Here we include some information about this
       module. Unfortunately we're including it with
       the function but it does support wikiwords like WikiWord.
    
       @brief
       This is a description of this method
       with some parameters and an inline note

       @{note, This is some more info here about
               this prototype}
       
       It also includes a warning about some random
       stuff.

       @{warning, This is a warning}

       And an inline table

       @{table,
       - One | Two
       - Three | Four
       }

       @param p1 [I] - The first parameter
       @param p2 [I] - The second parameter
       @param p3 [O] - The third parameter

       @return True on success

       @since
         This method was introduced in version 1.0

       @see
         For world for more information.

       @deprecated
         This function was deprecated in release 1.0

       @example
         hello()
    '''

    print "Hello "

def world(x=None,y=None,z=None):
    '''@h2 Section XYZ
       Some random info about section xyz.

       @brief
       This is a test method that doesn't really
       have a very good prototype
    '''


    print "world!"
