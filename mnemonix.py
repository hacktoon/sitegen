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

import argparse
import sys
import os

from axiom import Library
from exceptions import (ValuesNotDefinedError, PageExistsError, 
						SiteAlreadyInstalledError, FileNotFoundError,
						TemplateError, PageValueError)


VERSION = "0.2.0-beta"

def update(args):
	'''Read recursively every directory under path and
	outputs HTML/JSON for each page file'''
	
	lib = Library()
	try:
		specs = lib.get_specs()
		path = args.path or os.curdir
		lib.build(specs, path)
		
		categories = CategoryList()
		pages = PageList()
		for page in site.pages:
			page.render(env)
			#print("Generated page {!r}.".format(page.path))
		#site.generate_feeds()
	except (FileNotFoundError, ValuesNotDefinedError, 
			TemplateError, PageValueError) as e:
		sys.exit(e)
	
	if args.output_enabled:
		print("{}\nTotal of pages read: {}.".format("-" * 30, len(pages)))
		print("Total of pages generated: {}.\n".format(total_rendered))


def write(args):
	'''Create a new page in specified path'''
	path = args.path
	lib = Library()
	try:
		lib.create_page(path)
	except PageExistsError:
		sys.exit('Page {!r} already exists.'.format(path))
	
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "mnemonix build"!'.format(path))


def build(args):
	'''Install Mnemonic in the current folder'''
	print('Writing the plans for the wonder library Mnemonix...')
	print('Writing the plans for the wonder library Mnemonix...')
	
	lib = Library()
	try:
		lib.write_specs(args.path)
	except SiteAlreadyInstalledError as e:
		sys.exit(e)

	print('\nMnemonix was successfully installed!\n\n'
	'Next steps:\n1 - Edit the "config.me" file.\n'
	'2 - Run "mnemonix write [path]" to start creating pages!\n')


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

	parser_build = subparsers.add_parser('build', 
		help='build Mnemonic on current folder')
	parser_build.set_defaults(method=build)

	parser_write = subparsers.add_parser('write',
		help='create a empty page on the path specified')
	parser_write.add_argument("path")
	parser_write.set_defaults(method=write)

	parser_update = subparsers.add_parser('update', help='generate the pages')
	parser_update.add_argument("path")
	parser_update.set_defaults(method=update)

	args = parser.parse_args()	
	args.method(args)

if __name__ == '__main__':
	main()
