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


class TemplateError(Exception):
    pass


class NodeError(Exception):
    def __init__(self, msg, token, parser):
        self.token = token
        self.parser = parser
        super().__init__(msg)


class RuntimeError(NodeError):
    pass


class FileNotFoundError(NodeError):
    pass
