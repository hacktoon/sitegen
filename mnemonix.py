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
from alarum import (ValuesNotDefinedError, 
					PageExistsError, 
					SiteAlreadyInstalledError,
					FileNotFoundError,
					TemplateError,
					PageValueError)

def publish(args):
	'''Read recursively every directory under path and
	outputs HTML/JSON for each page file'''
	path = args.path or os.curdir
	lib = Library()
	try:
		lib.enter(path)
	except FileNotFoundError:
		sys.exit('No library were ever built in {!r}.'.format(path))

	try:
		pages = lib.get_pages(path)
		for page in pages:
			page.render(lib.meta)
			print("Generated page {!r}.".format(page.path))
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
		lib.enter(path)
	except FileNotFoundError:
		sys.exit('No library were ever built in {!r}.'.format(path))
	try:
		lib.write_page(path)
	except PageExistsError as e:
		sys.exit(e)
	
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "mnemonix build"!'.format(path))


def build(args):
	'''Builds Mnemonix in the current path'''
	print('Writing the plans for the wonder library Mnemonix...')
	print('Building the foundations of the library...')
	
	path = args.path or os.curdir
	lib = Library()
	try:
		lib.build(path)
	except SiteAlreadyInstalledError as e:
		sys.exit(e)

	print('\nMnemonix was successfully installed!\n\n'
	'Next steps:\n1 - Edit the "config.me" file.\n'
	'2 - Run "mnemonix write [path]" to start creating pages!\n')


def main():	
	description = 'The Static Publishing System of Nimus Ages.'
	parser = argparse.ArgumentParser(prog='mnemonix', 
		description=description)

	parser.add_argument("-o", "--output-enabled", 
						help="show generation messages",
						action="store_true")

	subparsers = parser.add_subparsers(title='Commands')

	parser_build = subparsers.add_parser('build', 
		help='build Mnemonix on current folder')
	parser_build.add_argument("path")
	parser_build.set_defaults(method=build)

	parser_write = subparsers.add_parser('write',
		help='create a empty page on the path specified')
	parser_write.add_argument("path")
	parser_write.set_defaults(method=write)

	parser_publish = subparsers.add_parser('publish', help='generate the pages')
	parser_publish.add_argument("path")
	parser_publish.set_defaults(method=publish)

	args = parser.parse_args()	
	args.method(args)

if __name__ == '__main__':
	main()
