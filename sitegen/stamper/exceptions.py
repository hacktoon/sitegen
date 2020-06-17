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


class TemplateError(Exception):
    pass


class BreakStatement(Exception):
    def __init__(self, partial_output='', token=None):
        self.partial_output = partial_output
        self.token = token


class FunctionReturn(Exception):
    def __init__(self, token, return_value=None):
        self.return_value = return_value
        self.token = token


class NodeError(Exception):
    def __init__(self, msg, token, parser):
        self.token = token
        self.parser = parser
        super().__init__(msg)


class FileNotFoundError(NodeError):
    pass
