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
import tempfile

from . import reader
from . import axiom

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


class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.template_content = 'test_template_content'
        self.file = tempfile.NamedTemporaryFile(mode='w+t', suffix='.tpl')
        self.file.write(self.template_content)

    def tearDown(self):
        self.file.close()

    def testTemplateLoading(self):
        template = axiom.Template(self.file.name)
        assert template.content == self.template_content
        assert template.path == self.file.name


if __name__ == '__main__':
    unittest.main()
