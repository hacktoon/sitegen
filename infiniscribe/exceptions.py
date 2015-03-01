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


class FileNotFoundError(Exception):
	pass

class SiteAlreadyInstalledError(Exception):
	pass

class PageExistsError(Exception):
	pass

class ValuesNotDefinedError(Exception):
	pass

class TemplateError(Exception):
	pass

class PageValueError(Exception):	
	pass