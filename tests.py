# encoding: utf-8

import unittest
import tempfile
import os

import ion
import quark
import photon

from datetime import datetime



class TestBasicBricks(unittest.TestCase):
    
    def test_read_file(self):
		content = 'this is first line\nthis is second line'
		content_lines = content.split('\n')
		
		fp = tempfile.NamedTemporaryFile(delete=False)
		fp.write(bytes(content, 'UTF-8'))
		fp.close()
		
		content_read = quark.read_file(fp.name)
		self.assertEqual(content, content_read)
		
		lines_read = quark.read_file(fp.name, 'list')
		self.assertEqual(content_lines, lines_read)
		

	def test_write_file(self):
		content = 'this is first line\nthis is second line'
		quark.write_file('test_file', content)
		
		with open('test_file') as f:
			test_content = f.read()
			self.assertEqual(test_content, content)


	'''
	def test_ion_parser(self):
		self.data_ion_file = 'title = Write your title here'
		'date = 2012-09-12 14:30:10'
		'content'
		'Write your content here'
		with open('/tmp/data.ion', 'w') as f:
			f.write(self.data_ion_file)
		ion_data = ion.parse_ion_file('/tmp/data.ion')
		data_dict = {
			'title': 'Write your title here',
			'date': '2012-09-12 14:30:10',
			'content': 'Write your content here'
		}
		self.assertEqual(ion_data, data_dict)

	
	def test_date_format(self):
		date = datetime()
		formated_date = quark.date_to_string('1347640769.0', '%d/%m/%Y')
		self.assertEqual('14/09/2012', formated_date)


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
	'''
	def tearDown(self):
		pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicBricks)
    unittest.TextTestRunner(verbosity=2).run(suite)
