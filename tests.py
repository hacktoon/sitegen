# encoding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import unittest

if __name__ == '__main__':
	testLoader = unittest.TestLoader()
	suite = testLoader.discover('.')
	runner = unittest.TextTestRunner()
	runner.run(suite)