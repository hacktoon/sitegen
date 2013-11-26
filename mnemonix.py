# coding: utf-8

'''
===============================================================================
Mnemonix - The Static Publishing System of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/mnemonix
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import sys
import argparse

from axiom import Site
from exceptions import (ValuesNotDefinedError, PageExistsError, 
						SiteAlreadyInstalledError, FileNotFoundError,
						TemplateError, PageValueError)


VERSION = "0.2.0-beta"

def gen(args):
	'''Read recursively every directory under path and
	outputs HTML/JSON for each page file'''
	
	site = Site()
	try:
		site.generate_pages()
		self.generate_feeds()
	except (FileNotFoundError, ValuesNotDefinedError, 
			TemplateError, PageValueError) as e:
		sys.exit(e)
	
	#if args.output_enabled:
	#	print("{}\nTotal of pages read: {}.".format("-" * 30, len(pages)))
	#	print("Total of pages generated: {}.\n".format(total_rendered))


def add(args):
	'''Create a new page in specified path'''
	
	path = args.path
	site = Site()
	try:
		site.write_page(path)
	except PageExistsError:
		sys.exit('Page {!r} already exists.'.format(path))
	
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "mnemonix gen"!'.format(path))


def init(args):
	'''Install Mnemonic in the current folder'''
	print('Installing Mnemonix...')
	
	site = Site()
	try:
		site.create()
	except SiteAlreadyInstalledError as e:
		sys.exit(e)

	print('\nMnemonix was successfully installed!\n\n'
	'Next steps:\n1 - Edit the "config.me" file.\n'
	'2 - Run "mnemonix add [path]" to start creating pages!\n')


def main():	
	description = 'The Static Publishing System of Nimus Ages.'
	parser = argparse.ArgumentParser(prog='mnemonix', 
		description=description)
	parser.add_argument('--version', action='version', 
						help="show current version and quits", 
						version=VERSION)

	parser.add_argument("-o", "--output-enabled", 
						help="show generation messages",
						action="store_true")

	subparsers = parser.add_subparsers(title='Commands')

	parser_init = subparsers.add_parser('init', 
		help='install Mnemonic on current folder')
	parser_init.set_defaults(method=init)

	parser_add = subparsers.add_parser('add', 
		help='create a empty page on the path specified')
	parser_add.add_argument("path")
	parser_add.set_defaults(method=add)

	parser_gen = subparsers.add_parser('gen', help='generate the pages')
	parser_gen.set_defaults(method=gen)

	args = parser.parse_args()	
	args.method(args)

if __name__ == '__main__':
	main()
