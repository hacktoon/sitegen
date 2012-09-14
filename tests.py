# encoding: utf-8

import ion
import unittest

class IonTest(unittest.TestCase):
    def setUp(self):
        self.data_ion_file = '''title = Write your title here
date = 12/09/2012
content
Write your content here'''
        open('/tmp/data.ion', 'w').write(self.data_ion_file)

    def test_ion_parser(self):
        ion_data = ion.parse_ion_file('/tmp/data.ion')
        data_dict = {
            'title': 'Write your title here',
            'date': '12/09/2012',
            'content': 'Write your content here'
        }
        self.assertEqual(ion_data, data_dict)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
