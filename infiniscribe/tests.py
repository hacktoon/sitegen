# encoding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import unittest
from . import reader

class TestReader(unittest.TestCase):

    def setUp(self):
        self.text = ('title = Post title\n'
            'date = 2012-09-12 14:30:10\n'
            'content\n'
            'example text')
        self.tokens = reader._tokenize(self.text)

    def testTokenizeSingleKeyValue(self):
        text = ' title  =  Post title\n  '
        tokens = reader._tokenize(text)
        self.assertEqual(tokens[0]['type'], 'name')
        self.assertEqual(tokens[0]['value'], 'title')

        self.assertEqual(tokens[1]['value'], '=')
        self.assertEqual(tokens[0]['type'], 'name')
        self.assertEqual(tokens[2]['value'], 'Post title')

    def testTokenizerContentValue(self):
        text = 'content\nExample text'
        tokens = reader._tokenize(text)
        self.assertEqual(tokens[0]['value'], 'Example text')


if __name__ == '__main__':
    unittest.main()