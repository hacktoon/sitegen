# coding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

class SiteAlreadyInstalledError(Exception):
	pass

class PageExistsError(Exception):
	pass

class TemplateError(Exception):
	pass

class PageValueError(Exception):
	pass
