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

from os import path

BASE_URL = 'http://localhost/'
TEMPLATES_DIR = 'templates'
DATA_DIR = 'data'
DATA_FILE = 'page.me'
CONFIG_FILE = 'config.me'
FEED_FILE = 'feed.xml'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TEMPLATE = 'default'
FEED_DIR = 'feed'
FEED_NUM = 8
TEMPLATES_EXT = '.tpl'
JSON_FILENAME = 'data.json'
HTML_FILENAME = 'index.html'

MODEL_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(MODEL_DIR, DATA_DIR)
