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

import os
from alarum import FileNotFoundError

def normalize(name):
	return name.replace(' ', '-').lower()

def urljoin(base, *slug):
	'''Custom URL join function to concatenate and add slashes'''
	fragments = [base]
	fragments.extend(filter(None, slug))
	return '/'.join(s.replace('\\', '/').strip('/') for s in fragments)

def bring_file(path):
	if not os.path.exists(path):
		raise FileNotFoundError('File {!r} couldn\'t be found!'.format(path))
	with open(path, 'r') as f:
		return f.read()

def write_file(path, content=''):
	if os.path.exists(path):
		f = open(path, 'r')
		current_content = f.read()
		if current_content == content:
			return
		f.close()
	f = open(path, 'w')
	f.write(content)
	f.close()
