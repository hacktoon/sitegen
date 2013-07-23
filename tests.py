# encoding: utf-8

import unittest
import os

import mnemonix
import axiom
import reader

from datetime import datetime

class TestFileHandlers(unittest.TestCase):

	def setUp(self):
		self.test_file_path = 'test_file'
		self.test_file = open(self.test_file_path, 'w')
		self.content = 'this is first line\nthis is second line'
		self.test_file.write(self.content)
		self.test_file.close()


	def testReadFile(self):
		content_read = axiom.read_file(self.test_file_path)
		self.assertEqual(self.content, content_read)
		

	def testWriteFile(self):
		content = 'Another version\nthis is another line'
		axiom.write_file(self.test_file_path, content)
		with open(self.test_file_path) as f:
			test_content = f.read()
			self.assertEqual(test_content, content)


	def tearDown(self):
		os.remove(self.test_file_path)


class TestHelpers(unittest.TestCase):

	def testFileParser(self):
		file_content = ('title = Write your title here\n'
	   'date = 2012-09-12 14:30:10\n'
	   'content\n'
	   'Write your content here')
		file_data = axiom.parse_input_file(file_content)
		data_dict = {
			'title': 'Write your title here',
			'date': '2012-09-12 14:30:10',
			'content': 'Write your content here'
		}
		self.assertEqual(file_data, data_dict)


	def testURLJoin(self):
		# append slash
		final = axiom.urljoin('http://localhost', '')
		self.assertEqual('http://localhost/', final)
		# concat url parts
		final = axiom.urljoin('http://localhost', 'base')
		self.assertEqual('http://localhost/base', final)
		# split extra slashes
		final = axiom.urljoin('http://localhost/', '/base/')
		self.assertEqual('http://localhost/base', final)

		
	def testExtractTags(self):
		tag_string = 'eletron,  neutron,  proton   '
		tag_list = ['eletron', 'neutron', 'proton']
		self.assertEqual(tag_list, axiom.extract_tags(tag_string))


if __name__ == '__main__':
	unittest.main()
