# encoding: utf-8

import unittest
import tempfile
import os

import ion
import quark
import photon

from datetime import datetime

class TestBasicBricks(unittest.TestCase):

	def testReadFile(self):
		content = 'this is first line\nthis is second line'
		fp = tempfile.NamedTemporaryFile(delete=False)
		fp.write(bytes(content, 'UTF-8'))
		fp.close()
		content_read = quark.read_file(fp.name)
		self.assertEqual(content, content_read)
		

	def testWriteFile(self):
		content = 'this is first line\nthis is second line'
		quark.write_file('test_file', content)
		with open('test_file') as f:
			test_content = f.read()
			self.assertEqual(test_content, content)


	def testIonParser(self):
		file_content = ('title = Write your title here\n'
	   'date = 2012-09-12 14:30:10\n'
	   'content\n'
	   'Write your content here')
		ion_data = quark.parse_ion_file(file_content)
		data_dict = {
			'title': 'Write your title here',
			'date': '2012-09-12 14:30:10',
			'content': 'Write your content here'
		}
		self.assertEqual(ion_data, data_dict)

	'''
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
