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

import reader
import axiom


VERSION = "0.2.0-beta"


def gen(args):
	'''Read recursively every directory under path and
	outputs HTML/JSON for each page file'''
	env = axiom.get_env()
	env['output_enabled'] = args.output_enabled
	pages = env['pages']
	if not pages:
		sys.exit('No pages to generate.')
	total_rendered = 0
	for page in pages.values():
		if 'draft' in page['props']:
			continue
		if not 'nojson' in page['props']:	
			reader.save_json(env, page)
		if not 'nohtml' in page['props']:
			reader.save_html(env, page)
			total_rendered += 1
	print("{}\nTotal of pages read: {}.".format("-" * 30, len(pages)))
	print("Total of pages generated: {}.\n".format(total_rendered))
	# after generating all pages, update feed
	reader.generate_feeds(env)


def add(args):
	path = args.path
	'''Create a new page in specified path'''
	# copy source file to new path
	file_path = axiom.create_page(path)
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "mnemonix gen"!'.format(file_path))


def init(args):
	'''Install Mnemonic in the current folder'''
	print('Installing Mnemonic...')
	axiom.create_site()
	print('\nMnemonic was successfully installed!\n\n'
	'Next steps:\n1 - Edit the "site" file.\n'
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
