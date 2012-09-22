# encoding: utf-8

import os
import unittest
import ion

class TestHelpers(unittest.TestCase):
    def test_ion_parser(self):
        self.data_ion_file = '''title = Write your title here
date = 12/09/2012
content
Write your content here'''
        with open('/tmp/data.ion', 'w') as f:
            f.write(self.data_ion_file)
        ion_data = ion.parse_ion_file('/tmp/data.ion')
        data_dict = {
            'title': 'Write your title here',
            'date': '12/09/2012',
            'content': 'Write your content here'
        }
        self.assertEqual(ion_data, data_dict)

    def test_date_format(self):
        formated_date = ion.date_format('1347640769.0', '%d/%m/%Y')
        self.assertEqual('14/09/2012', formated_date)

    def test_system_pathinfo(self):
        system_path = os.path.join(os.getcwd(), ion.CFG['system_dir'])
        config_path = os.path.join(system_path, ion.CFG['config_file'])
        pathinfo = ion.system_pathinfo()
        self.assertEqual((system_path, config_path), pathinfo)

    def test_build_style(self):
        permalink = 'http://localhost/'
        filenames = 'main.css, print.css'
        built_tags = ion.build_style_tags(filenames, permalink)
        model = '<link rel="stylesheet" type="text/css" href="url" />\n'
        result = ''
        for tag in filenames.split(','):
            url = permalink + tag.strip()
            result += model.replace('url', url)
        self.assertEqual(result, built_tags)
    
    def test_build_script(self):
        permalink = 'http://localhost/'
        filenames = 'main.js, jquery.js'
        built_tags = ion.build_script_tags(filenames, permalink)
        model = '<script src="url"></script>\n'
        result = ''
        for tag in filenames.split(','):
            url = permalink + tag.strip()
            result += model.replace('url', url)
        self.assertEqual(result, built_tags)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
