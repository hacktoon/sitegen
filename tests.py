# encoding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import unittest

if __name__ == '__main__':
	testLoader = unittest.TestLoader()
	suite = testLoader.discover('.')
	runner = unittest.TextTestRunner()
	runner.run(suite)