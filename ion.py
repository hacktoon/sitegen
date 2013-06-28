# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import sys

import photon  # rendering functions
import quark  # low level module, basic bricks

# obey the rules
if sys.version_info.major < 3:
	sys.exit('Zap! Ion requires Python 3!')


def ion_charge():
	'''Reads recursively every directory under path and
	outputs HTML/JSON for each data.ion file'''
	env = quark.get_env()
	pages = env['pages']
	if not pages:
		sys.exit('No pages to generate.')
	for page in pages.values():
		if 'norender' in page['props']:
			continue
		photon.save_json(env, page)
		photon.save_html(env, page)
	# after generating all pages, update feed
	photon.save_rss(env)


def ion_spark(path):
	'''Creates a new page in specified path'''
	# copy source file to new path
	file_path = quark.create_page(path)
	print('Page {!r} successfully created!'.format(path))
	print('Edit the file {!r} and call "ion charge"!'.format(file_path))


def ion_plug():
	'''Installs Ion in the current folder'''
	print('Installing Ion...')
	quark.create_site()
	print('\nIon was successfully installed!\n'
	'Run "ion spark [path]" to start creating pages!\n')


def ion_help():
	help_message = '''Usage:
	ion.py plug - Installs Ion on this folder.
	ion.py spark [path/to/folder] - Creates a empty page on path specified.
	ion.py charge [path/to/folder] - Generates HTML/JSON files of each \
folder under the path specified and its subfolders, recursively.
	ion.py help - Shows this help message.
	'''
	print(help_message)


if __name__ == '__main__':
	# first parameter - command
	try:
		command = sys.argv[1]
	except IndexError:
		ion_help()
		sys.exit()

	# second parameter - path
	# if not provided, defaults to current
	try:
		path = sys.argv[2]
	except IndexError:
		path = '.'

	if command == 'plug':
		ion_plug()
	elif command == 'spark':
		ion_spark(path)
	elif command == 'charge':
		ion_charge()
	elif command == 'help':
		ion_help()
	else:
		print('Zap! {0} is a very strange command!'.format(command))
		print(help_message)
