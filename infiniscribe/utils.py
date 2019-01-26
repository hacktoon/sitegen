# coding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import re
import os

def clear_path(path):
    return re.sub(r'^\.$|^\./|\.\\', '', path)

def read_file(path):
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
    with open(path, 'w') as f:
        f.write(content)

def urljoin(*fragments):
    '''Custom URL join function to concatenate and add slashes'''
    return '/'.join(fragments)
