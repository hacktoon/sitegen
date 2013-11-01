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


class FileNotFoundError(Exception):
	pass

class SiteAlreadyInstalledError(Exception):
	pass

class PageExistsError(Exception):
	pass

class ValuesNotDefinedError(Exception):
	pass
