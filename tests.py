# encoding: utf-8

import unittest
import tempfile
import os

import ion
import quark
import photon

from datetime import datetime

class TestFileHandlers(unittest.TestCase):

	def setUp(self):
		self.test_file_path = 'test_file'
		self.test_file = open(self.test_file_path, 'w')
		self.content = 'this is first line\nthis is second line'
		self.test_file.write(self.content)
		self.test_file.close()


	def testReadFile(self):
		content_read = quark.read_file(self.test_file_path)
		self.assertEqual(self.content, content_read)
		

	def testWriteFile(self):
		content = 'Another version\nthis is another line'
		quark.write_file(self.test_file_path, content)
		with open(self.test_file_path) as f:
			test_content = f.read()
			self.assertEqual(test_content, content)


	def tearDown(self):
		os.remove(self.test_file_path)


class TestHelpers(unittest.TestCase):

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


	def testURLJoin(self):
		# append slash
		final = quark.urljoin('http://localhost', '')
		self.assertEqual('http://localhost/', final)
		# concat url parts
		final = quark.urljoin('http://localhost', 'base')
		self.assertEqual('http://localhost/base', final)
		# split extra slashes
		final = quark.urljoin('http://localhost/', '/base/')
		self.assertEqual('http://localhost/base', final)

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

if __name__ == '__main__':
	unittest.main()
