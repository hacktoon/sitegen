# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import sys
import argparse

import photon  # rendering functions
import quark  # low level module, basic bricks


VERSION = "1.1.1"


def ion_gen(args):
	'''Reads recursively every directory under path and
	outputs HTML/JSON for each data.ion file'''
	env = quark.get_env()
	env['output_enabled'] = args.output_enabled
	pages = env['pages']
	if not pages:
		sys.exit('No pages to generate.')
	total_rendered = 0
	for page in pages.values():
		if 'norender' in page['props']:
			continue
		if not 'nojson' in page['props']:	
			photon.save_json(env, page)
		if not 'nohtml' in page['props']:
			photon.save_html(env, page)
			total_rendered += 1
	print("{}\nTotal of pages read: {}.".format("-" * 30, len(pages)))
	print("Total of pages generated: {}.\n".format(total_rendered))
	# after generating all pages, update feed
	photon.generate_feeds(env)


def ion_add(args):
	path = args.path
	'''Creates a new page in specified path'''
	# copy source file to new path
	file_path = quark.create_page(path)
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "ion gen"!'.format(file_path))


def ion_init(args):
	'''Installs Ion in the current folder'''
	print('Installing Ion...')
	quark.create_site()
	print('\nIon was successfully installed!\n\n'
	'Next steps:\n1 - Edit the "config.ion" file.\n'
	'2 - Run "ion add [path]" to start creating pages!\n')


def main():	
	description = 'A static site generator.'
	parser = argparse.ArgumentParser(prog='ion', 
		description=description)
	parser.add_argument('--version', action='version', 
						help="show current version and quits", 
						version=VERSION)

	parser.add_argument("-o", "--output-enabled", 
						help="show generation messages",
						action="store_true")

	subparsers = parser.add_subparsers(title='Commands')

	parser_init = subparsers.add_parser('init', 
		help='install Ion on current folder')
	parser_init.set_defaults(method=ion_init)

	parser_add = subparsers.add_parser('add', 
		help='create a empty page on the path specified')
	parser_add.add_argument("path")
	parser_add.set_defaults(method=ion_add)

	parser_gen = subparsers.add_parser('gen', help='generate the pages')
	parser_gen.set_defaults(method=ion_gen)

	args = parser.parse_args()
	args.method(args)


if __name__ == '__main__':
	main()
